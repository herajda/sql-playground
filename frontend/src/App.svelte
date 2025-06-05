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
  let modalWidth = 'auto'
  let modalHeight = 'auto'
  let results: any[] | null = null
  let columns: string[] = []
  let error: string | null = null

  function generateMermaid(
    tables: {
      name: string
      columns: { name: string; type: string }[]
      foreign_keys?: { from: string; to_table: string; to_column: string }[]
    }[]
  ) {
    const lines: string[] = ['erDiagram']
    const relations = new Set<string>()

    for (const table of tables) {
      lines.push(`  ${table.name} {`)
      for (const col of table.columns) {
        lines.push(`    ${col.type} ${col.name}`)
      }
      lines.push('  }')

      if (table.foreign_keys) {
        for (const fk of table.foreign_keys) {
          const rel = `${fk.to_table} ||--o{ ${table.name} : ${fk.from}`
          relations.add(rel)
        }
      }
    }

    relations.forEach((r) => lines.push(r))
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
      themeVariables: { fontSize: '12px' },
      er: {
        fontSize: 12,
        minEntityWidth: 100,
        minEntityHeight: 100,
        entityPadding: 10,
        nodeSpacing: 100,
        rankSpacing: 100
      },
    })
  })

  function loadSchema() {
    if (schemaInitialized) return
    schemaInitialized = true
    fetch('http://localhost:5000/api/schema')
      .then((r) => r.json())
      .then((data) => {
        const diagram = generateMermaid(data.tables)
        mermaid
          .render('schema', diagram, schemaContainer)
          .then((res: { svg: string; bindFunctions?: (parent: Element) => void }) => {
            schemaContainer.innerHTML = res.svg
            res.bindFunctions?.(schemaContainer)
            const svg = schemaContainer.querySelector('svg') as SVGSVGElement | null
            if (svg) {
              const bbox = svg.getBBox()
              modalWidth = Math.min(bbox.width + 200, window.innerWidth * 0.95) + 'px'
              modalHeight = Math.min(bbox.height + 100, window.innerHeight * 0.25) + 'px'
            }
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
    modalWidth = 'auto'
    modalHeight = 'auto'
  }
</script>

<main>
  <h1>SQL Playground</h1>
  <div class="editor" bind:this={editorContainer}></div>
  <div class="actions">
    <button on:click={execute}>Execute</button>
    <button on:click={openSchema}>Show Database Schema</button>
  </div>
  {#if error}
    <p style="color:red">{error}</p>
  {/if}
  {#if results !== null}
    {#if results.length}
      <table class="results-table" border="1">
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
    <div class="modal-overlay" on:click={closeSchema}>
      <div
        class="modal"
        on:click|stopPropagation
        style="width:{modalWidth}; height:{modalHeight}; max-width:95vw; max-height:95vh;"
      >
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
  .actions {
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .results-table {
    margin-left: auto;
    margin-right: auto;
  }
  .schema {
    margin-top: 0rem;
    text-align: left;
    overflow: auto;
  }
  .schema :global(svg) {
    width: 100%;
    height: auto;
    transform-origin: top left;
  }
  .schema :global(svg text) {
    font-size: 12px;
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
    max-width: 95vw;
    max-height: 95vh;
    overflow: auto;
  }

  .close {
    float: right;
  }
</style>
