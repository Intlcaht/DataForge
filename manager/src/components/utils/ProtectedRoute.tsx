// ProtectedRoute.tsx
import { getUser, login } from '@/api/OIDCService';
import { User } from 'oidc-client-ts';
import { JSX, useEffect, useState } from 'react';

/**
 * ProtectedRoute Component
 * 
 * This component serves as a wrapper for routes that require authentication.
 * It verifies that a user is authenticated before rendering its children.
 * If no user is found or the user's session has expired, it redirects to login.
 * 
 * @param {Object} props - Component properties
 * @param {JSX.Element} props.children - Child components to render when authenticated
 * @returns {JSX.Element} The protected content or a loading state
 */
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
    // Track the authenticated user state
    const [user, setUser] = useState<User | undefined>(undefined);
    // Track loading state to show appropriate feedback to users
    const [isLoading, setIsLoading] = useState<boolean>(true);
    // Optional: Track error state for better UX
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // RECOMMENDATION: Add error handling with try/catch
        const authenticateUser = async () => {
            try {
                setIsLoading(true);
                const currentUser = await getUser();
                
                if (!currentUser || currentUser.expired) {
                    // RECOMMENDATION: Log authentication failures for monitoring
                    console.log('User not authenticated or session expired, redirecting to login');
                    
                    // RECOMMENDATION: Add a small delay to ensure any state updates complete
                    // before redirecting to prevent potential memory leaks
                    setTimeout(() => login(), 100);
                } else {
                    // User is authenticated, update state
                    setUser(currentUser);
                }
            } catch (err) {
                // RECOMMENDATION: Handle potential errors from getUser()
                console.error('Authentication check failed:', err);
                setError('Failed to verify authentication status');
                
                // RECOMMENDATION: Consider a more graceful error handling approach
                // instead of immediate redirect on error
                setTimeout(() => login(), 1000);
            } finally {
                setIsLoading(false);
            }
        };

        authenticateUser();
        
        // RECOMMENDATION: Set up a refresh timer if tokens need periodic refresh
        const refreshInterval = setInterval(() => {
            authenticateUser();
        }, 300000); // Check every 5 minutes
        
        return () => clearInterval(refreshInterval);
    }, []);

    // RECOMMENDATION: Show different states based on loading/error conditions
    if (isLoading) {
        return (
            <div className="auth-loading-container">
                {/* RECOMMENDATION: Add a better loading indicator */}
                <div className="auth-loading-spinner"></div>
                <p>Verifying authentication status...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="auth-error-container">
                <p>Authentication Error: {error}</p>
                <button onClick={() => login()}>Return to Login</button>
            </div>
        );
    }

    // RECOMMENDATION: Add additional security checks if needed
    // For example, verify required roles or permissions
    if (user) {
        // RECOMMENDATION: Add role-based access control if needed
        // if (requiredRole && !user.profile.roles.includes(requiredRole)) {
        //    return <div>You don't have permission to access this page</div>;
        // }
        
        return children;
    }

    // Fallback loading state (should rarely hit this)
    return <div>Redirecting to login...</div>;
};

export default ProtectedRoute;