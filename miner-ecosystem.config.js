module.exports = {
  apps: [
    {
      name: `miner_proxy_server_${process.env.WALLET_HOTKEY || 'default'}`,
      script: "proxies/miner.py",
      interpreter: "python3",
      args: generateArgs(),
      env: getEnvVariables(),
      max_memory_restart: '2000M',
    },
    {
      name: `miner_server_${process.env.WALLET_HOTKEY || 'default'}`,
      script: "neurons/miner/core.py",
      interpreter: "python3",
      args: generateArgs(),
      env: getEnvVariables(),
      max_memory_restart: '2000M',
    },
    {
      name: "auto_update",
      script: "auto_update.py",
      interpreter: "python3",
      cron_restart: "*/1 * * * *",
      autorestart: false,
      env: {
        ...getEnvVariables(),
        NEURON_TYPE: "miner",
      },
    },
  ],
};

// Function to parse command-line arguments and override defaults
function generateArgs() {
  // Default arguments
  const defaultArgs = {
    "--wallet.hotkey": process.env.WALLET_HOTKEY || 'default',
    "--wallet.name": process.env.WALLET_NAME || 'default',
    "--subtensor.network": process.env.SUBTENSOR_NETWORK || 'finney',
    "--subtensor.chain_endpoint": process.env.SUBTENSOR_CHAIN_ENDPOINT || 'wss://entrypoint-finney.opentensor.ai:443',
    "--axon.port": process.env.AXON_PORT || 8091
  };

  // Parse additional arguments passed via `process.argv` after `--`
  const extraArgs = process.argv.slice(3); // Remove `pm2`, `start`, and `miner-ecosystem.config.js`
  for (let i = 0; i < extraArgs.length; i += 2) {
    const key = extraArgs[i];
    const value = extraArgs[i + 1];
    if (key && value) {
      defaultArgs[key] = value;
    }
  }

  // Convert the arguments object to an array of strings for `args` parameter
  return Object.entries(defaultArgs).flat();
}

// Function to get environment variables
function getEnvVariables() {
  return {
    WALLET_HOTKEY: process.env.WALLET_HOTKEY || "default",
    WALLET_NAME: process.env.WALLET_NAME || "default",
    SUBTENSOR_NETWORK: process.env.SUBTENSOR_NETWORK || "finney",
    SUBTENSOR_CHAIN_ENDPOINT: process.env.SUBTENSOR_CHAIN_ENDPOINT || "wss://entrypoint-finney.opentensor.ai:443",
    AXON_PORT: process.env.AXON_PORT || 8091
  };
}