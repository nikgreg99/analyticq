/**
 * Updates the page metadata including title and description
 * @param {string} title - The title to set for the page. Will be combined with site name if not already included
 * @param {string} description - The description to set in the meta description tag
 * @returns {void}
 *
 * @example
 * updatePageMetadata('Home', 'Welcome to our website')
 * // Sets document title to "Home | My App"
 * // Sets meta description to "Welcome to our website"
 */
export function updatePageMetadata(title, description, path) {
    const meta = window.SITE_METADATA || {
        siteName: 'My App',
        siteUrl: window.location.origin,
        defaultImage: '/images/default.jpg'
    };

    console.log(title);
    const formattedTitle = title.includes(meta.siteName)
        ? title
        : `${title} | ${meta.siteName}`;

    // Update document title
    document.title = formattedTitle;

    // Update meta description
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) {
        metaDesc.setAttribute('content', description);
    }

    if (path) {
        const fullUrl = `${meta.siteUrl}${path}`;

        // Update canonical link
        let canonicalLink = document.querySelector('link[rel="canonical"]');
        if (!canonicalLink) {
          canonicalLink = document.createElement('link');
          canonicalLink.setAttribute('rel', 'canonical');
          document.head.appendChild(canonicalLink);
        }
        canonicalLink.setAttribute('href', fullUrl);
      }
}
