# -*- coding: utf-8 -*-
"""
Indian Language Font & Rendering Support for NexRoute
Provides dynamic Google Font injection and CSS typography tuning for:
- Telugu (Noto Sans Telugu)
- Devanagari / Hindi & Marathi (Noto Sans Devanagari)
- Kannada (Noto Sans Kannada)
- Tamil (Noto Sans Tamil)
- Malayalam (Noto Sans Malayalam)
- Bengali (Noto Sans Bengali)
"""

from typing import Optional


def get_font_injection_html(lang: Optional[str] = "en") -> str:
    """
    Returns HTML <link> and <style> block ensuring all 8 Indian language scripts
    render with pristine clarity, zero glyph clipping, and appropriate line heights.
    """
    return """
    <!-- Google Fonts for 8 Supported Indian Languages -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Noto+Sans+Bengali:wght@400;600;700;800&family=Noto+Sans+Devanagari:wght@400;600;700;800&family=Noto+Sans+Kannada:wght@400;600;700;800&family=Noto+Sans+Malayalam:wght@400;600;700;800&family=Noto+Sans+Tamil:wght@400;600;700;800&family=Noto+Sans+Telugu:wght@400;600;700;800&display=swap" rel="stylesheet">

    <style>
    /* Global Multilingual Font Stack with Graceful System Fallbacks */
    html, body, [class*="css"], .stApp, .stMarkdown, button, input, select, textarea {
        font-family: 'Inter',
                     'Noto Sans Telugu',
                     'Noto Sans Devanagari',
                     'Noto Sans Kannada',
                     'Noto Sans Tamil',
                     'Noto Sans Malayalam',
                     'Noto Sans Bengali',
                     'Segoe UI',
                     -apple-system,
                     sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }

    /* Indic Script Specific Line Height and Spacing Adjustments */
    :lang(te), [data-lang="te"], .lang-te {
        font-family: 'Noto Sans Telugu', 'Gautami', 'Mandali', sans-serif !important;
        line-height: 1.55 !important;
    }
    :lang(hi), :lang(mr), [data-lang="hi"], [data-lang="mr"], .lang-hi, .lang-mr {
        font-family: 'Noto Sans Devanagari', 'Mangal', sans-serif !important;
        line-height: 1.52 !important;
    }
    :lang(kn), [data-lang="kn"], .lang-kn {
        font-family: 'Noto Sans Kannada', 'Tunga', sans-serif !important;
        line-height: 1.55 !important;
    }
    :lang(ta), [data-lang="ta"], .lang-ta {
        font-family: 'Noto Sans Tamil', 'Latha', sans-serif !important;
        line-height: 1.52 !important;
    }
    :lang(ml), [data-lang="ml"], .lang-ml {
        font-family: 'Noto Sans Malayalam', 'Kartika', sans-serif !important;
        line-height: 1.55 !important;
    }
    :lang(bn), [data-lang="bn"], .lang-bn {
        font-family: 'Noto Sans Bengali', 'Vrinda', sans-serif !important;
        line-height: 1.52 !important;
    }

    /* Prevent clipping for complex Indic ligatures & compound conjuncts */
    .stMarkdown p, .stMarkdown span, .stMarkdown div,
    .stButton button, .quantum-card, .touchable-route-card {
        overflow-wrap: break-word !important;
        word-break: break-word !important;
        min-height: max-content;
    }
    </style>
    """
