<script lang="ts">
  let query = ''
  let results: any[] | null = null
  let columns: string[] = []
  let error: string | null = null

  async function execute() {
    error = null
    results = null
    const res = await fetch('http://localhost:5000/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    })
    const data = await res.json()
    error = data.error
    columns = data.columns || []
    results = data.results || []
  }
</script>

<main>
  <h1>SQL Playground</h1>
  <textarea bind:value={query} rows="4" cols="80"></textarea>
  <br>
  <button on:click={execute}>Execute</button>
  {#if error}
    <p style="color:red">{error}</p>
  {/if}
  {#if results !== null}
    {#if results.length}
      <table border="1">
        <thead>
          <tr>
            {#each columns as col}
              <th>{col}</th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each results as row}
            <tr>
              {#each row as value}
                <td>{value}</td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p>No results.</p>
    {/if}
  {/if}
</main>
