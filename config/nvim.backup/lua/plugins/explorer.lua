local gh = require('plugin_utils')

-- Disable netrw (nvim-tree replaces it).
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1

vim.pack.add({ gh('nvim-tree/nvim-tree.lua') })

require('nvim-tree').setup({
  view = {
    side = 'left',
    width = 30,
  },
})
