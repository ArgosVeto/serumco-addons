window.klaroConfig = {
    privacyPolicy: '/politique_cookies',
    acceptAll: true,
    apps : [
        {
            name : 'essential',
            default: true,
            required: true,
            // title : 'Essential',
            // purposes: ['essential'],
        },
        {
            name : 'cookies-analytics',
            default: true,
            // title : 'Cookies Analytics',
            // purposes: ['statistics'],
            cookies : [
                [/^_ga/i],
                [/^_gat/i],
                [/^_gid/i],
            ],
        },
        {
            name : 'cookies-fonctionnal',
            default: true,
            // title : 'Cookies Fonctionnals',
            // purposes: ['statistics'],
        },
        {
            name : 'cookies-advertisings',
            default: true,
            // title : 'Cookies Advertisings',
            // purposes: ['statistics'],
        },

        {
            name : 'cookies-socials',
            default: true,
            // title : 'Cookies Socials',
            // purposes: ['statistics'],

        },
    ],
    translations: {
        // If you erase the "consentModal" translations, Klaro will use the
        // bundled translations.
        en: {
            consentModal: {
                description:
                    "We use cookies and similar technologies. Some cookies are essential for this websites functionality, some help us to understand how you use our site and to improve your experience.",
            },
            consentNotice: {
                learnMore: "Settings",
            },
            'google-analytics': {
                description: 'Google Analytics is a tracking tool for traffic analysis of websites. We use Google Analytics to understand the user behaviour of visitors to our website and to improve the general user experience.',
            },
            'essential': {
                description: 'Essentials serve the functionality of the website. We use Essential cookies for general functionality and navigation on the site.',
            },
            purposes: {
                statistics: 'Visitor Statistics',
                essential: 'Essential'
            }
        },
        fr: {
            poweredBy:"",
            acceptAll: "Accepter tout",
            acceptSelected: "Accepter",
            consentModal: {
                description:
                    "Nous utilisons les cookies afin de vous proposer un service amélioré et personnalisé. Vous pouvez les accepter ou les refuser en totalité ou par typologie.\n" +
                    "Afin de poursuivre votre navigation sur le site, nous vous invitons à faire un choix concernant le dépôt de cookies.",
            },
            consentNotice: {
                learnMore: "Paramêtres",
                description: "En poursuivant votre navigation, vous acceptez notre usage des cookies conformément à notre politique de gestion des Données personnelles et cookies. Vous pouvez à tout moment gérer vos préférences en modifiant vos paramètres cookies.",

            },
            'essential': {
                description: 'Essentiels',
            },
            'cookies-analytics': {
                description: 'Les cookies analytiques',
            },
            'cookies-fonctionnal': {
                description: 'Les cookies fonctionnels',
            },
            'cookies-advertisings': {
                description: 'Les cookies publicitaires',
            },
            'cookies-socials': {
                description: 'Les cookies réseaux sociaux',
            },

            purposes: {
                statistics: 'Visitor Statistics',
                essential: 'Essential'
            }
        }
    }
};
