local gh = require('plugin_utils')

vim.pack.add({ gh('akinsho/toggleterm.nvim') })

require('toggleterm').setup({
  direction = 'vertical',
  size = function(term)
    return term.direction == 'vertical' and math.floor(vim.o.columns * 0.4) or 15
  end,
})
