-- Cache compiled Lua modules for faster startup.
vim.loader.enable()

-- Set Space as the leader key. This must be set before plugins load.
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '

vim.g.have_nerd_font = true

-- ============================================================
-- FILETYPE DETECTION
-- Neovim doesn't ship built-in detection for every extension.
-- Registering this here ensures both LSP (tinymist) and Treesitter
-- correctly recognize .typ files as 'typst'.
-- ============================================================
vim.filetype.add({
  extension = { typ = 'typst' },
})

-- ============================================================
-- EDITOR APPEARANCE AND BEHAVIOR
-- ============================================================
vim.o.number = true
vim.o.relativenumber = true
vim.o.mouse = 'a'
vim.o.showmode = false

-- Use the system clipboard. Schedule this because clipboard setup can
-- otherwise add a little startup overhead.
vim.schedule(function()
  vim.o.clipboard = 'unnamedplus'
end)

vim.o.breakindent = true

-- Persist undo history between Neovim sessions.
vim.o.undofile = true

-- Search case-insensitively, unless the search contains uppercase letters.
vim.o.ignorecase = true
vim.o.smartcase = true

-- Always reserve space for diagnostics/signs so the text doesn't shift.
vim.o.signcolumn = 'yes'

vim.o.updatetime = 250
vim.o.timeoutlen = 300

-- Open new splits to the right and below.
vim.o.splitright = true
vim.o.splitbelow = true

-- Show whitespace that is otherwise easy to miss.
vim.o.list = true
vim.opt.listchars = {
  tab = '» ',
  trail = '·',
  nbsp = '␣',
}

-- Preview the result of substitutions in a split as you type.
vim.o.inccommand = 'split'

vim.o.cursorline = true

-- Keep some context visible above and below the cursor when scrolling.
vim.o.scrolloff = 10

-- Ask for confirmation instead of failing commands when there are unsaved changes.
vim.o.confirm = true
