import { createContext, useContext, useState, ReactNode, useEffect } from 'react'

/**
 * Type definition for the HeaderSlotContext
 * Defines the shape of the context that will be used to manage header slot content
 * @property {ReactNode} slot - The current React node rendered in the header slot
 * @property {Function} setSlot - Function to set/update the content of the header slot
 * @property {Function} clearSlot - Convenience function to remove content from the header slot
 */
type HeaderSlotContextType = {
    slot: ReactNode
    setSlot: (node: ReactNode) => void
    clearSlot: () => void
}

/**
 * Create a new React context for managing header slot content
 * Initially undefined, will be populated by the provider
 * This context allows components to access and modify header content from anywhere in the component tree
 */
const HeaderSlotContext = createContext<HeaderSlotContextType | undefined>(undefined)

/**
 * Provider component that wraps the application to make header slot functionality available
 * Creates and manages the state for the header slot content
 * 
 * @param {Object} props - Component props
 * @param {ReactNode} props.children - Child components that will have access to this context
 * @returns {JSX.Element} Context provider wrapping the children
 */
export const HeaderSlotProvider = ({ children }: { children: ReactNode }) => {
    // Initialize state to store the current header slot content, initially null (empty)
    const [slot, setSlotState] = useState<ReactNode>(null)

    /**
     * Function to update the header slot with new content
     * @param {ReactNode} node - The React node to render in the header slot
     */
    const setSlot = (node: ReactNode) => setSlotState(node)

    /**
     * Convenience function to clear/empty the header slot
     * Simply calls setSlotState with null to remove any content
     */
    const clearSlot = () => setSlotState(null)

    // Provide the current slot state and manipulation functions to all children
    return (
        <HeaderSlotContext.Provider value={{ slot, setSlot, clearSlot }}>
            {children}
        </HeaderSlotContext.Provider>
    )
}

/**
 * Custom hook to access the header slot context from any component
 * 
 * This hook:
 * 1. Retrieves the current context value
 * 2. Throws an error if used outside of HeaderSlotProvider
 * 3. Returns the context with type safety
 * 
 * The ESLint comment disables the react-refresh/only-export-components rule
 * because hooks are not components but are exported
 * 
 * @returns {HeaderSlotContextType} The header slot context object with slot state and functions
 * @throws {Error} If used outside of a HeaderSlotProvider
 */
// eslint-disable-next-line react-refresh/only-export-components
export const useHeaderSlot = (Component) => {
    // Get the current context value
    const ctx = useContext(HeaderSlotContext)

    // Safety check: ensure the hook is used within a provider
    if (!ctx) throw new Error('useHeaderSlot must be used within HeaderSlotProvider')

    const { setSlot, clearSlot } = ctx

    useEffect(() => {
        if (Component) {
            setSlot(<Component />)
        }
        return () => clearSlot()
    }, [setSlot, clearSlot, Component])

    // Return the context value to the calling component
    return ctx
}

function Header() {
    const { slot } = useHeaderSlot(undefined)
    return (
        <header className="border-b border-gray-200 flex items-center justify-between px-4 py-2">
            <div className="flex items-center">
                <h1 className="text-xl font-semibold">BK Management</h1>
                <div className="ml-4 relative">
                    <select className="border rounded px-3 py-1 text-sm pr-8">
                        <option>Production</option>
                        <option>Development</option>
                        <option>Testing</option>
                    </select>
                </div>
            </div>
            <div className="flex items-center gap-4">
                {slot}
                <button className="p-2 text-gray-500 hover:text-gray-700 relative">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                </button>
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                        <span className="text-xs font-medium">JS</span>
                    </div>
                    <span className="text-sm font-medium">John Smith</span>
                </div>
            </div>
        </header>
    )
}

export default Header