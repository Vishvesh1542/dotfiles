-- ============================================================
-- RUN CURRENT FILE
-- Compiles/runs the current file in a dedicated, reused terminal
-- pane (separate from the interactive terminal on <leader>q), so
-- output always lands in the same place. Add an entry per filetype
-- to `runners` to support more languages. The keymap for this
-- lives in keymaps.lua.
-- ============================================================
local Terminal = require('toggleterm.terminal').Terminal

-- A plain persistent shell — no `cmd` here, so the job never exits and
-- we can keep sending new commands into it.
local run_term = Terminal:new({
  id = 99, -- distinct from the <leader>q terminal
  direction = 'vertical',
  close_on_exit = false,
})

-- Each runner gets `file` (full path) and `stem` (path without
-- extension) and returns the shell command as a single string.
local runners = {
  c = function(file, stem)
    local out = '/tmp/' .. vim.fn.fnamemodify(stem, ':t')
    return 'gcc ' .. vim.fn.shellescape(file) .. ' --output ' .. vim.fn.shellescape(out)
      .. ' && ' .. vim.fn.shellescape(out)
  end,

  typst = function(file, stem)
    local out = '/tmp/' .. vim.fn.fnamemodify(stem, ':t') .. '.pdf'
    return 'typst watch ' .. vim.fn.shellescape(file) .. ' ' .. vim.fn.shellescape(out) .. ' --open'
  end,

  -- Example of adding another language later:
  -- python = function(file, _)
  --   return 'python3 ' .. vim.fn.shellescape(file)
  -- end,
}

local M = {}

function M.run_current_file()
  local file = vim.fn.expand('%:p')
  local stem = vim.fn.expand('%:p:r')
  local filetype = vim.bo.filetype

  local runner = runners[filetype]
  if not runner then
    vim.notify('No run command configured for filetype: ' .. filetype, vim.log.levels.WARN)
    return
  end

  vim.cmd('write') -- save before running

  if not run_term:is_open() then
    run_term:open()
  end

  -- `clear` wipes the previous run's output first, since it doesn't matter.
  run_term:send('clear; ' .. runner(file, stem), true) -- true = keep focus in your code
end

return M
