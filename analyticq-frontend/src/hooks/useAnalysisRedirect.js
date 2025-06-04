import { useNavigate } from "react-router-dom";
import { getContextByRepoName } from "../services/contextService";

/**
 * Custom hook for handling context-based navigation and redirection in the application.
 * @returns {Object} An object containing the redirectToContext function.
 * @property {Function} redirectToContext - Redirects to the context page based on repository name.
 * @property {Function} redirectToContext.params.repoName - The name of the repository to fetch context for.
 * @property {Object} [redirectToContext.params.options] - Optional configuration for the redirect.
 * @property {boolean} [redirectToContext.params.options.replace=false] - Whether to replace the current history entry.
 * @property {string} [redirectToContext.params.options.fallbackPath="/contexts"] - Fallback path if context is not found.
 * @throws {Error} When there's an error fetching the context.
 */
export const useAnalysisRedirect = () => {

    const navigate = useNavigate();

    const redirectToContext = async(repoName, options = {}) => {

        const { replace = false, fallbackPath = "/contexts"} = options;

        if(!repoName) {
            console.warn("No repository name provided for context redirection.");
            navigate(fallbackPath, { replace });
            return;
        }

        try{

            const extractedRepoName = repoName.includes('/')
                ? repoName.split('/').pop().replace('.git', '')
                : repoName;

            const context = await getContextByRepoName(extractedRepoName);
            if (context) {
                navigate(`/contexts/${context.id}`, { replace });

                if(context && context.id){
                    navigate(`/contexts/${context.id}/analysis`, { replace });
                }
                else {
                    console.warn(`Context not found for repository: ${extractedRepoName}`);
                    navigate(fallbackPath, { replace });
                }
            }
        } catch (error) {
            console.error("Error fetching context:", error);
            navigate(fallbackPath, { replace });
        }

    }
    return {
        redirectToContext,
    };
}
