<script lang="ts">
  let password = ''
  let dbs: string[] = []
  let activeDb = ''
  let uploadFile: File | null = null
  let error: string | null = null
  let loggedIn = false

  async function login() {
    error = null
    const res = await fetch('http://localhost:5000/api/admin/databases', {
      headers: { 'X-Admin-Password': password }
    })
    if (!res.ok) {
      error = 'Invalid password'
      loggedIn = false
      return
    }
    const data = await res.json()
    dbs = data.databases
    activeDb = data.active
    loggedIn = true
  }

  async function upload() {
    if (!uploadFile) return
    const fd = new FormData()
    fd.append('file', uploadFile)
    await fetch('http://localhost:5000/api/admin/upload', {
      method: 'POST',
      headers: { 'X-Admin-Password': password },
      body: fd
    })
    await login()
  }

  async function activate(name: string) {
    await fetch('http://localhost:5000/api/admin/activate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Password': password
      },
      body: JSON.stringify({ name })
    })
    await login()
  }
</script>

<main>
  <h1>Admin</h1>
  {#if !loggedIn}
    <input
      type="password"
      placeholder="Password"
      bind:value={password}
    />
    <button on:click={login}>Login</button>
    {#if error}
      <p style="color:red">{error}</p>
    {/if}
  {:else}
    <button on:click={() => (loggedIn = false)}>Logout</button>
    <p>Active DB: {activeDb}</p>
    <ul>
      {#each dbs as db}
        <li>
          {db}
          {#if db !== activeDb}
            <button on:click={() => activate(db)}>Activate</button>
          {/if}
        </li>
      {/each}
    </ul>
    <input type="file" accept=".db" on:change={(e) => (uploadFile = e.target.files[0])} />
    <button on:click={upload}>Upload</button>
  {/if}
</main>

<style>
  .admin {
    margin-top: 1rem;
    text-align: left;
  }
  input[type='password'] {
    margin-right: 0.5rem;
  }
</style>
