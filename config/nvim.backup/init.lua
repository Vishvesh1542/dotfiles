-- ============================================================
-- ENTRY POINT
-- Top-level editor config lives directly in lua/. Anything that
-- installs a plugin lives in lua/plugins/. This file only decides
-- *what* loads and *in what order*.
-- ============================================================

require('options')

-- Plugins (installed via the built-in vim.pack).
require('plugins.pack')         -- vim.pack build-step hooks (must load first)
require('plugins.ui')           -- colorscheme, statusline, git signs, which-key, mini.nvim
require('plugins.telescope')    -- fuzzy finder
require('plugins.terminal')     -- right-hand terminal panel
require('plugins.explorer')     -- left-hand file tree
require('plugins.lsp')          -- language servers via mason + lspconfig
require('plugins.formatting')   -- conform.nvim
require('plugins.completions')  -- blink.cmp + LuaSnip
require('plugins.snippets')     -- custom snippets
require('plugins.treesitter')   -- syntax highlighting/indent
require('plugins.run')          -- run current file
require('plugins.spectre')      -- project-wide search and replace

-- Editor behavior that doesn't need plugins loaded first.
require('diagnostics')
require('keymaps')              -- every keybinding lives here
require('autocmds')
require('typst')                -- optional: only loads anything if `typst` is installed
