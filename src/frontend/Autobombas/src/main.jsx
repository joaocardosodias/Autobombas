import React from 'react'
import ReactDOM from 'react-dom/client'
import { AppRouter } from './router'
import { Toaster } from 'sonner'
import './style.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppRouter />
    <Toaster richColors position='top-center' />
  </React.StrictMode>,
)