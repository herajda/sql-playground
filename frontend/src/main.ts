import { mount } from 'svelte'
import './app.css'
import App from './App.svelte'
import Admin from './Admin.svelte'

const target = document.getElementById('app')!
const Component = window.location.pathname === '/admin' ? Admin : App

const app = mount(Component, {
  target,
})

export default app
