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
  let showSchema = false
  let schemaInitialized = false
  let results: any[] | null = null
  let columns: string[] = []
  let error: string | null = null

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
      themeVariables: { fontSize: '32px' },
      er: {
        fontSize: 32,
        minEntityWidth: 200,
        minEntityHeight: 120,
        entityPadding: 15
      },
      nodeSpacing: 40,
      rankSpacing: 40
    })
  })

  function loadSchema() {
    if (schemaInitialized) return
    schemaInitialized = true
    fetch('http://localhost:5000/api/schema')
      .then((r) => r.json())
      .then((data) => {
        const diagram = generateMermaid(data.tables)
        mermaid.render('schema', diagram, schemaContainer).then((res: { svg: string; bindFunctions?: (parent: Element) => void }) => {
          schemaContainer.innerHTML = res.svg
          res.bindFunctions?.(schemaContainer)
        })
      })
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

  function openSchema() {
    showSchema = true
    loadSchema()
  }

  function closeSchema() {
    showSchema = false
    schemaInitialized = false
    if (schemaContainer) schemaContainer.innerHTML = ''
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
  <button on:click={openSchema}>Show Database Schema</button>
  {#if showSchema}
    <div class="modal-overlay" on:click={closeSchema}>
      <div class="modal" on:click|stopPropagation>
        <button class="close" on:click={closeSchema}>Close</button>
        <div class="schema" bind:this={schemaContainer}></div>
      </div>
    </div>
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
    overflow: auto;
  }
  .schema :global(svg) {
    width: 100%;
    height: auto;
    transform: scale(1.5);
    transform-origin: top left;
  }
  .schema :global(svg text) {
    font-size: 32px;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: var(--background, #fff);
    padding: 1rem;
    border-radius: 8px;
    max-width: 90%;
    max-height: 90%;
    overflow: auto;
  }

  .close {
    float: right;
  }
</style>
