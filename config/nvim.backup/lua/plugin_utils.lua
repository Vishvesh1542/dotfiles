-- Most plugins live on GitHub, so this saves repeating the full URL
-- everywhere. Usage: gh('folke/tokyonight.nvim')
return function(repo)
  return 'https://github.com/' .. repo
end
