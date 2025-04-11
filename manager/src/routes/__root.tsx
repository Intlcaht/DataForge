import Header, { HeaderSlotProvider } from '@/components/layout/Header'
import Sidebar from '@/components/layout/Sidebar'
import { createRootRoute, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'

export const Route = createRootRoute({
  component: () => (
    <>
      <main className='[--sidebar-width:12rem] [--header-height:6rem] flex h-screen bg-zinc-100'>
        <Sidebar />
        <section className='flex-1 overflow-auto'>
          <HeaderSlotProvider>
            <>
              <Header />
              <Outlet />
            </>
          </HeaderSlotProvider>
        </section>
      </main>
      <TanStackRouterDevtools />
    </>
  ),
})