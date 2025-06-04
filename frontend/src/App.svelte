<script lang="ts">
  import { onMount } from 'svelte'
  import { EditorState } from '@codemirror/state'
  import { EditorView, basicSetup } from 'codemirror'
  import { sql } from '@codemirror/lang-sql'

  let query = ''
  let editorContainer: HTMLDivElement
  let results: any[] | null = null
  let columns: string[] = []
  let error: string | null = null

  onMount(() => {
    const state = EditorState.create({
      doc: query,
      extensions: [
        basicSetup,
        sql(),
        EditorView.updateListener.of((v) => {
          if (v.docChanged) {
            query = v.state.doc.toString()
          }
        })
      ]
    })
    new EditorView({ state, parent: editorContainer })
  })

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
  <div class="editor" bind:this={editorContainer}></div>
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

<style>
  .editor {
    border: 1px solid #ccc;
    min-height: 5rem;
  }
</style>
