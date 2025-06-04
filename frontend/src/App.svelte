<script lang="ts">
  import { onMount } from 'svelte'
  import { EditorState } from '@codemirror/state'
  import { EditorView, basicSetup } from 'codemirror'
  import { sql } from '@codemirror/lang-sql'
  import { keymap } from '@codemirror/view'
  import { acceptCompletion } from '@codemirror/autocomplete'
  import mermaid from 'mermaid/dist/mermaid.esm.mjs'

  let query = ''
  let editorContainer: HTMLDivElement
  let schemaContainer: HTMLDivElement
  let results: any[] | null = null
  let columns: string[] = []
  let error: string | null = null
  let showSchema = false

  function generateMermaid(tables: { name: string; columns: { name: string; type: string }[] }[]) {
    const lines = ['erDiagram']
    for (const table of tables) {
      lines.push(`  ${table.name} {`)
      for (const col of table.columns) {
        lines.push(`    ${col.type} ${col.name}`)
      }
      lines.push('  }')
    }
    return lines.join('\n')
  }

  onMount(() => {
    const state = EditorState.create({
      doc: query,
      extensions: [
        basicSetup,
        sql(),
        keymap.of([{ key: 'Tab', run: acceptCompletion }]),
        EditorView.updateListener.of((v) => {
          if (v.docChanged) {
            query = v.state.doc.toString()
          }
        })
      ]
    })
    new EditorView({ state, parent: editorContainer })

    mermaid.initialize({
      startOnLoad: false,
      themeVariables: { fontSize: '20px' },
      er: {
        fontSize: 20,
        minEntityWidth: 120,
        minEntityHeight: 80,
        entityPadding: 15
      },
      nodeSpacing: 40,
      rankSpacing: 40
    })
    fetch('http://localhost:5000/api/schema')
      .then((r) => r.json())
      .then((data) => {
        const diagram = generateMermaid(data.tables)
        mermaid.render('schema', diagram, schemaContainer).then((res: { svg: string; bindFunctions?: (parent: Element) => void }) => {
          schemaContainer.innerHTML = res.svg
          res.bindFunctions?.(schemaContainer)
        })
      })
  })

  function toggleSchema() {
    showSchema = !showSchema
  }

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
  <button on:click={toggleSchema} style="margin-left: 1rem">
    {showSchema ? 'Hide Schema' : 'Show Database Schema'}
  </button>
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
  {#if showSchema}
    <h2>Database Schema</h2>
    <div class="schema" bind:this={schemaContainer}></div>
  {/if}
</main>

<style>
  .editor {
    border: 1px solid #ccc;
    min-height: 5rem;
    text-align: left;
  }
  .editor :global(.cm-gutters) {
    display: none;
  }
  .schema {
    margin-top: 1rem;
    text-align: left;
  }
  .schema :global(svg) {
    width: 100%;
    height: auto;
  }
  .schema :global(svg text) {
    font-size: 20px;
  }
</style>
