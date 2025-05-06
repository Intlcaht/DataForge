
import { Activity, Database, Home, Settings, Shield, Variable } from 'lucide-react'
import { SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, Sidebar as UISidebar } from '../ui/sidebar'

function Sidebar() {

  // const router = useRouter();

  // Menu items.
  const { menu, system } = {
    "menu": [
      {
        title: "Dashboard",
        url: "/",
        icon: Home,
      },
      {
        title: "Databases",
        url: "/databases",
        icon: Database,
      },
      {
        title: "Env Vars",
        url: "/env",
        icon: Variable,
      },
    ],
    "system": [
      {
        title: "Configuration",
        url: "#",
        icon: Settings,
      },
      {
        title: "Security",
        url: "#",
        icon: Shield,
      },
      {
        title: "Monitoring",
        url: "#",
        icon: Activity,
      }
    ]
  }

  return (
    <UISidebar>
      <SidebarHeader >
        <div className="bg-indigo-600 text-white p-1 rounded">
          <span className="font-bold">LOGO</span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup >
          <SidebarGroupLabel>Menu</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menu.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup >
          <SidebarGroupLabel>System</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {system.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter />
    </UISidebar>
  )
}

export default Sidebar