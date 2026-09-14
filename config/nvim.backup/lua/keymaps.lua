-- ============================================================
-- GENERAL EDITING
-- ============================================================
vim.keymap.set('n', '<Esc>', '<cmd>nohlsearch<CR>', { desc = 'Clear search highlight' })

-- Delete without clobbering the yank register (use x to cut instead).
vim.keymap.set({ 'n', 'v' }, 'd', '"_d', { desc = 'Delete without yanking' })
vim.keymap.set('n', 'D', '"_D', { desc = 'Delete to end of line without yanking' })

-- ============================================================
-- WINDOW NAVIGATION
-- ============================================================
vim.keymap.set('n', '<C-h>', '<C-w><C-h>', { desc = 'Move to left window' })
vim.keymap.set('n', '<C-l>', '<C-w><C-l>', { desc = 'Move to right window' })
vim.keymap.set('n', '<C-j>', '<C-w><C-j>', { desc = 'Move to lower window' })
vim.keymap.set('n', '<C-k>', '<C-w><C-k>', { desc = 'Move to upper window' })

-- ============================================================
-- TERMINAL MODE
-- ============================================================
vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

-- ============================================================
-- SIDE PANELS (explorer / quick terminal)
-- ============================================================
vim.keymap.set('n', '<leader>e', '<cmd>NvimTreeToggle<CR>', { desc = '[E]xplorer: toggle file tree' })
vim.keymap.set({ 'n', 't' }, '<leader>q', '<cmd>ToggleTerm<CR>', { desc = '[Q]uick terminal' })

-- ============================================================
-- DIAGNOSTICS
-- ============================================================
vim.keymap.set('n', '<leader>kq', vim.diagnostic.setloclist, { desc = 'Open diagnostic list' })

-- ============================================================
-- FORMATTING
-- ============================================================
vim.keymap.set({ 'n', 'v' }, '<leader>f', function()
  require('conform').format({ async = true })
end, { desc = '[F]ormat buffer' })

-- ============================================================
-- RUN CURRENT FILE
-- ============================================================
vim.keymap.set('n', '<leader>r', function()
  require('plugins.run').run_current_file()
end, { desc = '[R]un current file' })

-- ============================================================
-- SEARCH AND REPLACE (project-wide)
-- ============================================================
vim.keymap.set('n', '<leader>sR', function()
  require('spectre').open()
end, { desc = '[S]earch and [R]eplace (project-wide)' })

-- ============================================================
-- TELESCOPE SEARCH
-- ============================================================
local builtin = require('telescope.builtin')

vim.keymap.set('n', '<leader>sh', builtin.help_tags, { desc = '[S]earch [H]elp' })
vim.keymap.set('n', '<leader>sk', builtin.keymaps, { desc = '[S]earch [K]eymaps' })
vim.keymap.set('n', '<leader>sf', builtin.find_files, { desc = '[S]earch [F]iles' })
vim.keymap.set('n', '<leader>ss', builtin.builtin, { desc = '[S]earch [S]elect Telescope' })
vim.keymap.set({ 'n', 'v' }, '<leader>sw', builtin.grep_string, { desc = '[S]earch current [W]ord' })
vim.keymap.set('n', '<leader>sg', builtin.live_grep, { desc = '[S]earch by [G]rep' })
vim.keymap.set('n', '<leader>sd', builtin.diagnostics, { desc = '[S]earch [D]iagnostics' })
vim.keymap.set('n', '<leader>sr', builtin.resume, { desc = '[S]earch [R]esume' })
vim.keymap.set('n', '<leader>s.', builtin.oldfiles, { desc = '[S]earch Recent Files' })
vim.keymap.set('n', '<leader>sc', builtin.commands, { desc = '[S]earch [C]ommands' })
vim.keymap.set('n', '<leader><leader>', builtin.buffers, { desc = 'Find existing buffers' })

vim.keymap.set('n', '<leader>/', function()
  builtin.current_buffer_fuzzy_find(require('telescope.themes').get_dropdown({
    winblend = 10,
    previewer = false,
  }))
end, { desc = 'Search current buffer' })

vim.keymap.set('n', '<leader>s/', function()
  builtin.live_grep({ grep_open_files = true, prompt_title = 'Live Grep in Open Files' })
end, { desc = '[S]earch [/] in Open Files' })

vim.keymap.set('n', '<leader>sn', function()
  builtin.find_files({ cwd = vim.fn.stdpath('config'), follow = true })
end, { desc = '[S]earch [N]eovim files' })

-- ============================================================
-- LSP
-- Fires whenever a language server attaches to a buffer.
-- ============================================================
vim.api.nvim_create_autocmd('LspAttach', {
  group = vim.api.nvim_create_augroup('lsp-keymaps', { clear = true }),
  callback = function(event)
    local buf = event.buf
    local map = function(keys, func, desc, mode)
      vim.keymap.set(mode or 'n', keys, func, { buffer = buf, desc = 'LSP: ' .. desc })
    end

    map('grn', vim.lsp.buf.rename, '[R]e[n]ame')
    map('gra', vim.lsp.buf.code_action, '[G]oto Code [A]ction', { 'n', 'x' })
    map('grD', vim.lsp.buf.declaration, '[G]oto [D]eclaration')

    map('grr', builtin.lsp_references, '[G]oto [R]eferences')
    map('gri', builtin.lsp_implementations, '[G]oto [I]mplementation')
    map('grd', builtin.lsp_definitions, '[G]oto [D]efinition')
    map('gO', builtin.lsp_document_symbols, 'Open Document Symbols')
    map('gW', builtin.lsp_dynamic_workspace_symbols, 'Open Workspace Symbols')
    map('grt', builtin.lsp_type_definitions, '[G]oto [T]ype Definition')

    local client = vim.lsp.get_client_by_id(event.data.client_id)
    if client and client:supports_method('textDocument/inlayHint', buf) then
      map('<leader>th', function()
        vim.lsp.inlay_hint.enable(not vim.lsp.inlay_hint.is_enabled({ bufnr = buf }))
      end, '[T]oggle Inlay [H]ints')
    end
  end,
})

-- ============================================================
-- SMART TAB / SHIFT-TAB
-- Completion is NOT handled here — accept with <C-space> instead
-- (see completions.lua). Priority order for <Tab>:
--   1. Skip past ONE closing bracket/quote ahead of the cursor,
--      ignoring spaces in between. Checked before snippet-jump so
--      it always hops just one character, even inside an active
--      snippet's placeholder (e.g. $|$ -> $$|, not straight to the
--      snippet's next tabstop).
--   2. Otherwise, jump/expand a snippet, if one is active.
--   3. Otherwise, jump to the end of the current word, if the
--      cursor sits in the middle of one (letters on both sides).
--   4. Otherwise, insert a normal tab.
-- ============================================================
local closers = { [')'] = true, [']'] = true, ['}'] = true, ['"'] = true, ["'"] = true, ['`'] = true, ['*'] = true, ['$'] = true }

vim.keymap.set('i', '<Tab>', function()
  local line = vim.api.nvim_get_current_line()
  local row, col = unpack(vim.api.nvim_win_get_cursor(0))

  -- 1. Skip past a closer ahead of the cursor, ignoring spaces in between.
  local spaces, closer_char = line:sub(col + 1):match('^(%s*)(.)')
  if closer_char and closers[closer_char] then
    return vim.api.nvim_win_set_cursor(0, { row, col + #spaces + 1 })
  end

  -- 2. Jump/expand a snippet, if one is active.
  local luasnip = require('luasnip')
  if luasnip.expand_or_jumpable() then
    return luasnip.expand_or_jump()
  end

  -- 3. Jump to the end of the word if the cursor sits inside one.
  local prev_char = line:sub(col, col)
  local next_char = line:sub(col + 1, col + 1)
  if prev_char:match('%w') and next_char:match('%w') then
    local rest_of_word = line:sub(col + 1):match('^%w*')
    return vim.api.nvim_win_set_cursor(0, { row, col + #rest_of_word })
  end

  -- 4. Otherwise, insert a normal tab.
  vim.api.nvim_feedkeys(vim.api.nvim_replace_termcodes('<Tab>', true, false, true), 'n', false)
end, { desc = 'Smart tab: skip closer / snippet-jump / skip word / insert tab' })

vim.keymap.set('i', '<S-Tab>', function()
  local luasnip = require('luasnip')
  if luasnip.jumpable(-1) then
    return luasnip.jump(-1)
  end
  vim.api.nvim_feedkeys(vim.api.nvim_replace_termcodes('<C-d>', true, false, true), 'n', false)
end, { desc = 'Smart shift-tab: snippet-jump-back / de-indent' })

-- ============================================================
-- RELOAD CONFIG
-- ============================================================
vim.keymap.set('n', '<leader>kr', function()
  -- Clear only your own modules from Lua's cache (not third-party
  -- plugins), then re-run init.lua fresh.
  for name in pairs(package.loaded) do
    if name == 'options' or name == 'diagnostics' or name == 'autocmds'
      or name == 'keymaps' or name == 'typst' or name == 'plugin_utils'
      or name:match('^plugins%.') then
      package.loaded[name] = nil
    end
  end

  vim.cmd('source $MYVIMRC')
  vim.notify('Config reloaded', vim.log.levels.INFO)
end, { desc = '[K]onfig [R]eload' })
