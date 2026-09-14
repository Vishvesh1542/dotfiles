-- Auto-compile `.typ` files in the background with `typst watch`.
-- Skip entirely if typst isn't installed.
if vim.fn.executable('typst') == 0 then
  return
end

local output_dir = '/tmp/typst'

---@type table<string, { proc: vim.SystemObj, stopping: boolean }>
local watchers = {}

local function handle_line(name, line)
  if line:match('^compiled successfully') then
    vim.notify(name .. ': compiled successfully', vim.log.levels.INFO)
  elseif line:match('^compiled with %d+ warning') then
    vim.notify(name .. ': ' .. line, vim.log.levels.WARN)
  elseif line:match('^compiled with %d+ error') or line:match('^error:') then
    vim.notify(name .. ': ' .. line, vim.log.levels.ERROR)
  end
end

local function on_output(file)
  local name = vim.fn.fnamemodify(file, ':t')
  return function(_, data)
    if not data then
      return
    end
    vim.schedule(function()
      for line in data:gmatch('[^\r\n]+') do
        handle_line(name, line)
      end
    end)
  end
end

local function start_watcher(file)
  if watchers[file] then
    return
  end

  vim.fn.mkdir(output_dir, 'p')
  local output = output_dir .. '/' .. vim.fn.fnamemodify(file, ':t:r') .. '.pdf'
  local state = { stopping = false }

  local ok, proc = pcall(vim.system, { 'typst', 'watch', file, output }, {
    stdout = on_output(file),
    stderr = on_output(file),
  }, function(result)
    watchers[file] = nil
    if not state.stopping and result.code ~= 0 then
      vim.schedule(function()
        vim.notify(vim.fn.fnamemodify(file, ':t') .. ': Typst watcher exited unexpectedly', vim.log.levels.ERROR)
      end)
    end
  end)

  if not ok then
    vim.notify('Failed to start Typst watcher for ' .. vim.fn.fnamemodify(file, ':t'), vim.log.levels.ERROR)
    return
  end

  state.proc = proc
  watchers[file] = state
end

local function stop_watcher(file)
  local state = watchers[file]
  if not state then
    return
  end
  state.stopping = true
  state.proc:kill('sigterm')
  watchers[file] = nil
end

local group = vim.api.nvim_create_augroup('typst-watch', { clear = true })

vim.api.nvim_create_autocmd({ 'BufReadPost', 'BufNewFile' }, {
  group = group,
  pattern = '*.typ',
  callback = function(args)
    local file = vim.api.nvim_buf_get_name(args.buf)
    if file ~= '' then
      start_watcher(file)
    end
  end,
})

vim.api.nvim_create_autocmd('BufDelete', {
  group = group,
  pattern = '*.typ',
  callback = function(args)
    local file = vim.api.nvim_buf_get_name(args.buf)
    if file ~= '' then
      stop_watcher(file)
    end
  end,
})

vim.api.nvim_create_autocmd('VimLeavePre', {
  group = group,
  callback = function()
    for file in pairs(watchers) do
      stop_watcher(file)
    end
  end,
})
