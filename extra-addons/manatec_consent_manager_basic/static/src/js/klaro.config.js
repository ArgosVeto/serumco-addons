var klaroConfig = {
    testing: false,
    elementID: 'klaro',
    storageMethod: 'cookie',
    storageName: 'klaro',
    htmlTexts: false,
    cookieDomain: '.odoo.com',
    cookieExpiresAfterDays: 30,
    default: false,
    mustConsent: false,
    acceptAll: true,
    hideDeclineAll: false,
    hideLearnMore: false,
    translations: {
        /*
        The `zz` key contains default translations that will be used as fallback values.
            This can e.g. be useful for defining a fallback privacy policy URL.
        */
        zz: {
            privacyPolicyUrl: '/privacy',

        },

        en: {
            privacyPolicyUrl: '/privacy',
            consentModal: {
                description:
                    'Here you can see and customize the information that we collect about you. ' +
                    'Entries marked as "Example" are just for demonstration purposes and are not ' +
                    'really used on this website.',
            },
            purposes: {
                analytics: {
                    title: 'Analytics'
                },
                security: {
                    title: 'Security'
                },
                livechat: {
                    title: 'Livechat'
                },
                advertising: {
                    title: 'Advertising'
                },
                styling: {
                    title: 'Styling'
                },
                social: {
                    title: 'Social'
                },
            },
        },
        fr: {
            privacyPolicyUrl: '/privacy',
            consentModal: {
                description:
                    '[TEXTE A PERSONNALISER]',
            },
            purposes: {
                analytics: {
                    title: 'Google Analytics',
                    description: '[Google Analytics TEXT]',
                },
                security: {
                    title: 'Securité'
                },
                livechat: {
                    title: 'Livechat'
                },
                advertising: {
                    title: 'Partenaires publicitaires',
                    description: '[Partenaires publicitaires TEXT]',
                },
                styling: {
                    title: 'Styling'
                },
                social: {
                    title: 'Réseaux sociaux',
                    description: '[Réseaux sociaux TEXT]',
                },
                basic: {
                    title: 'Essentiels',
                    description: '[Essentiel TEXT]',
                },
            },
        },
    },
    services: [
                {
            name: 'essential',
            default: true,
            translations: {
                zz: {
                    title: 'Essential'
                },
                en: {
                    description: 'Basic is a simple service to blablabla '
                },
                fr: {
                    description: '[Essentiel TEXT_2]'
                },
            },
            purposes: ['basic'],

            cookies: [
                [/^_pk_.*$/, '/', 'klaro.kiprotect.com'],
                [/^_pk_.*$/, '/', 'localhost'],
                'piwik_ignore',
            ],
            required: true,
            optOut: false,
            onlyOnce: true,
        },
        {
            name: 'google_analytic',
            default: true,
            translations: {
                zz: {
                    title: 'Google Analytics'
                },
                en: {
                    description: 'Google Analytic is a simple service to blablabla'
                },
                fr: {
                    description: '[Google Analytics TEXT_2]'
                },
            },
            purposes: ['analytics'],

            cookies: [
                [/^_pk_.*$/, '/', 'klaro.kiprotect.com'],
                [/^_pk_.*$/, '/', 'localhost'],
                'piwik_ignore',
            ],
            required: false,
            optOut: false,
            onlyOnce: true,
        },
        {
            name: 'google_ads',
            default: true,
            translations: {
                zz: {
                    title: 'Google Adds'
                },
                en: {
                    description: 'Google Adds is a simple, self-hosted analytics service.'
                },
                fr: {
                    description: '[Google ADDS TEXT]'
                },
            },
            purposes: ['advertising'],

            cookies: [
                [/^_pk_.*$/, '/', 'klaro.kiprotect.com'],
                [/^_pk_.*$/, '/', 'localhost'],
                'piwik_ignore',
            ],
            required: false,
            optOut: false,
            onlyOnce: true,
        },
        {
            name: 'twitter',
            default: true,
            translations: {
                zz: {
                    title: 'Twitter'
                },
                en: {
                    description: 'Twitter is a simple, self-hosted analytics service.'
                },
                fr: {
                    description: '[Twitter TEXT]'
                },
            },
            purposes: ['social'],

            cookies: [
                [/^_pk_.*$/, '/', 'klaro.kiprotect.com'],
                [/^_pk_.*$/, '/', 'localhost'],
                'piwik_ignore',
            ],
            required: false,
            optOut: false,
            onlyOnce: true,
        },
        {
            name: 'facebook',
            default: true,
            translations: {
                zz: {
                    title: 'Facebook'
                },
                en: {
                    description: 'Facebook is a simple, self-hosted analytics service.'
                },
                fr: {
                    description: '[Facebook TEXT]'
                },
            },
            purposes: ['social'],

            cookies: [
                [/^_pk_.*$/, '/', 'klaro.kiprotect.com'],
                [/^_pk_.*$/, '/', 'localhost'],
                'piwik_ignore',
            ],
            required: false,
            optOut: false,
            onlyOnce: true,
        },
    ],
};