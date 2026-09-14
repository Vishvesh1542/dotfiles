-- ============================================================
-- SNIPPETS
-- Snippets live one file per filetype under lua/snippets/ (e.g.
-- snippets/typst.lua, snippets/rust.lua). Each file returns a table:
--
--   return {
--     autosnippets = { ... },  -- expand instantly as you type the trigger
--     snippets     = { ... },  -- expand via <Tab> / the completion menu
--   }
--
-- Both keys are optional. To support a new filetype, just add a new
-- file here — nothing in this loader needs to change.
-- ============================================================
local ls = require('luasnip')

ls.config.setup({
  enable_autosnippets = true,
})

local snippets_dir = vim.fn.stdpath('config') .. '/lua/snippets'

for _, path in ipairs(vim.fn.glob(snippets_dir .. '/*.lua', false, true)) do
  local filetype = vim.fn.fnamemodify(path, ':t:r')
  local mod = require('snippets.' .. filetype)

  if mod.snippets and #mod.snippets > 0 then
    ls.add_snippets(filetype, mod.snippets)
  end

  if mod.autosnippets and #mod.autosnippets > 0 then
    ls.add_snippets(filetype, mod.autosnippets, { type = 'autosnippets' })
  end
end
