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

    loadSchema()
  })

  function loadSchema() {
    if (!schemaContainer) return
    fetch('http://localhost:5000/api/schema')
      .then((r) => r.json())
      .then((data) => {
        const diagram = generateMermaid(data.tables)
        mermaid
          .render('schema', diagram, schemaContainer)
          .then((res: { svg: string; bindFunctions?: (parent: Element) => void }) => {
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

</script>

<main>
  <h1>SQL Playground</h1>
  <div class="layout">
    <div class="left">
      <div class="editor-section">
        <h2>Textbox for the SQL Commands</h2>
        <div class="editor" bind:this={editorContainer}></div>
      </div>
      <div class="schema-section">
        <h2>The ER/UML Diagram</h2>
        <div class="schema" bind:this={schemaContainer}></div>
      </div>
    </div>
    <div class="middle">
      <button class="execute" on:click={execute}>EXECUTE</button>
    </div>
    <div class="right">
      <h2>The Results Table</h2>
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
    </div>
  </div>
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
  .layout {
    margin-top: 1rem;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 1rem;
    align-items: flex-start;
  }

  .left {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    flex: 1;
  }

  .editor-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .schema-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow: auto;
  }

  .middle {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .results-table {
    margin-left: auto;
    margin-right: auto;
    width: 100%;
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
</style>
