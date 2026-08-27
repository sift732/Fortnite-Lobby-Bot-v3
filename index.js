const { readFile, writeFile } = require('fs').promises;
const { Client } = require('fnbr');

(async () => {
  let auth;

  try {
    auth = {
      deviceAuth: JSON.parse(
        await readFile('./deviceAuth.json', 'utf8')
      )
    };
  } catch {
    auth = {
      authorizationCode: async () =>
        Client.consoleQuestion('Please enter an authorization code: ')
    };
  }

  const client = new Client({ auth });

  client.on('deviceauth:created', async (deviceAuth) => {
    await writeFile(
      './deviceAuth.json',
      JSON.stringify(deviceAuth, null, 2)
    );

    console.log('Device Auth saved.');
  });

  await client.login();

  console.log(`Logged in as ${client.user.self.displayName}`);
})();
