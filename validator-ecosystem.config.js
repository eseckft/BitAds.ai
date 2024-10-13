module.exports = {
  apps: [
    {
      name: `validator_proxy_server_${process.env.WALLET_HOTKEY}`,
      script: "proxies/validator.py",
      interpreter: "python3",
      args: [
        "--wallet.hotkey", process.env.WALLET_HOTKEY,
        "--wallet.name", process.env.WALLET_NAME,
        "--subtensor.network", process.env.SUBTENSOR_NETWORK,
        "--subtensor.chain_endpoint", process.env.SUBTENSOR_CHAIN_ENDPOINT
      ],
      env: {
        WALLET_HOTKEY: process.env.WALLET_HOTKEY || "default",
        WALLET_NAME: process.env.WALLET_NAME || "default",
        SUBTENSOR_NETWORK: process.env.SUBTENSOR_NETWORK || "finney",
        SUBTENSOR_CHAIN_ENDPOINT: process.env.SUBTENSOR_CHAIN_ENDPOINT || "wss://entrypoint-finney.opentensor.ai:443"
      }
    },
    {
      name: `validator_server_${process.env.WALLET_HOTKEY}`,
      script: "neurons/validator/core.py",
      interpreter: "python3",
      args: [
        "--wallet.hotkey", process.env.WALLET_HOTKEY,
        "--wallet.name", process.env.WALLET_NAME,
        "--subtensor.network", process.env.SUBTENSOR_NETWORK,
        "--subtensor.chain_endpoint", process.env.SUBTENSOR_CHAIN_ENDPOINT
      ],
      env: {
        WALLET_HOTKEY: process.env.WALLET_HOTKEY || "default",
        WALLET_NAME: process.env.WALLET_NAME || "default",
        SUBTENSOR_NETWORK: process.env.SUBTENSOR_NETWORK || "finney",
        SUBTENSOR_CHAIN_ENDPOINT: process.env.SUBTENSOR_CHAIN_ENDPOINT || "wss://entrypoint-finney.opentensor.ai:443"
      }
    },
    {
      name: "auto_update",
      script: "auto_update.sh",
      interpreter: "python3",
      cron_restart: "*/1 * * * *",
      autorestart: false,
      env: {
        WALLET_HOTKEY: process.env.WALLET_HOTKEY || "default",
        WALLET_NAME: process.env.WALLET_NAME || "default",
        SUBTENSOR_NETWORK: process.env.SUBTENSOR_NETWORK || "finney",
        SUBTENSOR_CHAIN_ENDPOINT: process.env.SUBTENSOR_CHAIN_ENDPOINT || "wss://entrypoint-finney.opentensor.ai:443"
      }
    }
  ]
};