<script lang="ts">
import { EditorState } from '@codemirror/state'
import { EditorView, basicSetup } from 'codemirror'
import { sql } from '@codemirror/lang-sql'
import { keymap } from '@codemirror/view'
import { acceptCompletion } from '@codemirror/autocomplete'
import { afterUpdate } from 'svelte'

  let password = ''
  let dbs: string[] = []
  let activeDb = ''
  let uploadFile: File | null = null
  let error: string | null = null
  let loggedIn = false
  let createName = ''
  let createSQL = ''
  let schemaFile: File | null = null
  let openaiRequest = ''
  let readOnly = true
  let loading = false
  let editorContainer: HTMLDivElement
  let editorInitialized = false
  let showCreateModal = false
  let createStep = 1
  let createOption: 'sql' | 'file' | 'openai' = 'sql'

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
    await loadSettings()
  }

  async function loadSettings() {
    const res = await fetch('http://localhost:5000/api/admin/settings', {
      headers: { 'X-Admin-Password': password }
    })
    if (res.ok) {
      const data = await res.json()
      readOnly = data.read_only
    }
  }

  async function toggleReadOnly() {
    await fetch('http://localhost:5000/api/admin/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Password': password
      },
      body: JSON.stringify({ read_only: readOnly })
    })
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

  async function remove(name: string) {
    await fetch('http://localhost:5000/api/admin/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Password': password
      },
      body: JSON.stringify({ name })
    })
    await login()
  }

  async function createDb() {
    await fetch('http://localhost:5000/api/admin/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Password': password
      },
      body: JSON.stringify({ name: createName, schema: createSQL })
    })
    createName = ''
    await login()
  }

  async function createDbFromFile() {
    if (!schemaFile) return
    const fd = new FormData()
    fd.append('file', schemaFile)
    fd.append('name', createName)
    await fetch('http://localhost:5000/api/admin/create_from_file', {
      method: 'POST',
      headers: { 'X-Admin-Password': password },
      body: fd
    })
    createName = ''
    schemaFile = null
    await login()
  }

  async function createDbWithOpenAI() {
    loading = true
    try {
      await fetch('http://localhost:5000/api/admin/openai_create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Admin-Password': password
        },
        body: JSON.stringify({ name: createName, prompt: openaiRequest })
      })
      createName = ''
      openaiRequest = ''
      await login()
    } finally {
      loading = false
    }
  }

  function openCreateModal() {
    createName = ''
    createSQL = ''
    schemaFile = null
    openaiRequest = ''
    createStep = 1
    createOption = 'sql'
    editorInitialized = false
    showCreateModal = true
  }

  function closeCreateModal() {
    showCreateModal = false
  }

  async function handleCreate() {
    if (createOption === 'sql') {
      await createDb()
    } else if (createOption === 'file') {
      await createDbFromFile()
    } else {
      await createDbWithOpenAI()
    }
    showCreateModal = false
  }

  function initEditor() {
    if (editorInitialized || !editorContainer) return
    const state = EditorState.create({
      doc: createSQL,
      extensions: [
        basicSetup,
        sql(),
        keymap.of([{ key: 'Tab', run: acceptCompletion }]),
        EditorView.updateListener.of((v) => {
          if (v.docChanged) {
            createSQL = v.state.doc.toString()
          }
        })
      ]
    })
    new EditorView({ state, parent: editorContainer })
    editorInitialized = true
  }

  afterUpdate(() => {
    if (loggedIn && showCreateModal && createStep === 2 && createOption === 'sql') {
      initEditor()
    }
  })
</script>

<main class="admin">
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
    <label>
      <input type="checkbox" bind:checked={readOnly} on:change={toggleReadOnly} />
      Read Only Mode
    </label>
    <table class="db-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each dbs as db}
          <tr class:active={db === activeDb}>
            <td>{db}</td>
            <td>
              {#if db === activeDb}
                Active
              {:else}
                <button on:click={() => activate(db)}>Activate</button>
              {/if}
            </td>
            <td>
              {#if db !== 'playground.db'}
                <button on:click={() => remove(db)}>Delete</button>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
    <input
      type="file"
      accept=".db"
      on:change={(e) => {
        const input = e.target as HTMLInputElement
        uploadFile = input.files?.[0] || null
      }}
    />
    <button on:click={upload}>Upload</button>

    <button on:click={openCreateModal}>Create Database</button>
    {/if}

  {#if showCreateModal}
    <div class="modal-overlay" on:click={closeCreateModal}>
      <div class="modal" on:click|stopPropagation>
        {#if createStep === 1}
          <h2>Name Database</h2>
          <input
            type="text"
            placeholder="Name (example.db)"
            bind:value={createName}
          />
          <div class="actions">
            <button on:click={() => (createStep = 2)}>Next</button>
            <button on:click={closeCreateModal}>Cancel</button>
          </div>
        {:else}
          <h2>Choose Creation Method</h2>
          <select bind:value={createOption}>
            <option value="sql">Enter SQL</option>
            <option value="file">Upload SQL File</option>
            <option value="openai">Use OpenAI</option>
          </select>
          {#if createOption === 'sql'}
            <div class="editor" bind:this={editorContainer}></div>
          {:else if createOption === 'file'}
            <input
              type="file"
              accept=".sql,.txt"
              on:change={(e) => {
                const input = e.target as HTMLInputElement
                schemaFile = input.files?.[0] || null
              }}
            />
          {:else}
            <textarea
              rows="3"
              placeholder="Describe the desired database"
              bind:value={openaiRequest}
            ></textarea>
          {/if}
          <div class="actions">
            <button on:click={handleCreate}>Create</button>
            <button on:click={closeCreateModal}>Cancel</button>
          </div>
        {/if}
      </div>
    </div>
  {/if}
  </main>
  {#if loading}
    <div class="loading-overlay">
      <div class="loading-text">LOADING ...</div>
    </div>
  {/if}

<style>
  .admin {
    margin-top: 1rem;
    text-align: left;
  }
  input[type='password'] {
    margin-right: 0.5rem;
  }

  .editor {
    border: 1px solid #ccc;
    min-height: 5rem;
    text-align: left;
    margin-top: 0.5rem;
  }
  .editor :global(.cm-gutters) {
    display: none;
  }

  .file-create {
    margin-top: 0.5rem;
  }

  textarea {
    width: 100%;
    margin-top: 0.5rem;
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

  .actions {
    margin-top: 0.5rem;
    display: flex;
    gap: 0.5rem;
  }

  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1100;
    color: #fff;
    font-size: 1.5rem;
  }

  .loading-text {
    animation: blink 1s linear infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  .db-table {
    border-collapse: collapse;
    margin-top: 0.5rem;
    width: 100%;
  }

  .db-table th,
  .db-table td {
    border: 1px solid #ccc;
    padding: 0.25rem 0.5rem;
    text-align: left;
  }

  .db-table tr.active {
    background-color: rgba(100, 108, 255, 0.2);
  }
</style>
