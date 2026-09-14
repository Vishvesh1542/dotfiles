return {
  {
    "saghen/blink.cmp",
    opts = {
      keymap = {
        preset = "default",
        ["<CR>"] = { "fallback" },
        ["<C-tab>"] = { "select_and_accept", "fallback" },
      },
    },
  },
}
