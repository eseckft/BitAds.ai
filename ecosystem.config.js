module.exports = {
  apps: [

  ],
  deploy: {
    local: {
      host: 'localhost',
      ref: 'origin/fiber',
      repo: 'https://github.com/eseckft/BitAds.ai.git',
      path: 'BitAds.ai',
      'pre-setup': 'echo "This is a pre-setup command"',
      'pre-deploy': 'echo "This is a pre-deploy command"',
    },
  },
};