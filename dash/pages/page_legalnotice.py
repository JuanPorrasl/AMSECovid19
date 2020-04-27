import os

import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State 

from app import app

lorem=html.P([
    "A compléter",
    html.Br(),
    html.Br(),
    ]
)

txt_notice=[
        html.H5("1. Site presentation."),
        html.P([
            "Pursuant to Article 6 of Law No. 2004-575 of 21 June 2004 on confidence in the digital economy, users of the www.jda-conseil.fr website are informed of the identity of the various parties involved in its implementation and monitoring:",
            html.Br(),
            html.U("Owner:")," The content is under MIT License. The domain name belongs to Junior Data Analysts",
            html.Br(),
            html.U("Site Architecture:")," Python 3.7, Plotly, Dash",
            html.Br(),
            html.U("Responsible publication:")," The work is carried out by students of Aix-Marseille School of Economics under the supervision of the teaching staff",
            html.Br(),
            html.U("Site developed by:")," Thomas Pical, Juan Porras, Eduardo Leite Kropiwiec, Alvaro Sanchez, Ana gabriela Prada",
            html.Br(),
            html.U("Site put online by:")," Hervé Mignot",
            html.Br(),
            html.U("Host:")," OVH",
        ]),
        html.H5("2. General conditions of use of the site and the services offered."),
        html.P([
            "Use of the covid19.jda-conseil.fr site implies full and complete acceptance of the general conditions of use described below. These conditions of use may be modified or supplemented at any time, users of the covid19.jda-conseil.fr site are therefore invited to consult them regularly",
            html.Br(),
            "This site is normally accessible to users at all times. However, an interruption for technical maintenance may be decided without prior notice",
            html.Br(),
            "The covid19.jda-conseil.fr website is updated regularly. In the same way, the legal notices may be modified at any time: they are nevertheless binding on the user, who is invited to refer to them as often as possible in order to take note of them",
        ]),
        html.H5("3. Description of services provided."),
        html.P([
            "The covid19.jda-conseil.fr website aims to provide a dashboard of indicators focusing on the coronavirus crisis of 2020. The site strives to provide information that is as accurate as possible. However, it cannot be held responsible for omissions, inaccuracies and shortcomings in the update, whether caused by itself or by the third party partners who provide it with this information. All the information indicated on the covid19.jda-conseil.fr website is given for information purposes only, and is subject to change. Furthermore, the information on the covid19.jda-conseil.fr site is not exhaustive. They are given subject to modifications having been made since their setting on line",
            ]),
        html.H5("4. Contractual limitations on technical data."),
        html.P([
            "The site uses Python 3.7 technology as well as numerous packages, the main ones being Dash and Plotly. The website cannot be held responsible for any material damage related to the use of the site. In addition, the user of the site undertakes to access the site using recent, virus-free equipment and with a latest-generation, up-to-date browser",
            ]),
        html.H5("5. Intellectual property and counterfeits."),
        html.P([
            "Copyright © 2020, Covid19 - AMSE Student Dashboard",
            "Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:",
            html.Br(),
            "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.",
            html.Br(),
            "The Software is provided 'as is', without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders X be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software",
            html.Br(),
            "Except as contained in this notice, the name of the AMSE Student Dashboard shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from the AMSE Student Dashboard",
            ]),
        html.H5("6. Limitations of liability."),
        html.P([
            "Covid19 - AMSE Student Dashboard cannot be held responsible for any direct or indirect damage caused to the user's equipment when accessing the Covid19 - AMSE Student Dashboard website, resulting either from the use of equipment that does not meet the specifications indicated in point 4, or from the occurrence of a bug or incompatibility. Covid19 - AMSE Student Dashboard shall also not be liable for indirect damages (such as loss of business or loss of opportunity) arising out of the use of the covid19.jda-conseil.fr website. Interactive areas (possibility to ask questions in the contact area) are available to users. Covid19 - AMSE Student Dashboard reserves the right to delete, without prior notice, any content posted in this space that contravenes the legislation applicable in France, in particular the provisions relating to data protection. If need be, Covid19 - AMSE Student Dashboard also reserves the right to question the civil and/or penal responsibility of the user, in particular in the event of a message of a racist, insulting, defamatory or pornographic nature, whatever the medium used (text, photograph...)",
            ]),
        html.H5("7. Management of personal data."),
        html.P([
            "In France, personal data is notably protected by law n° 78-87 of January 6, 1978, law n° 2004-801 of August 6, 2004, article L. 226-13 of the Penal Code and the European Directive of October 24, 1995. When using the covid19.jda-conseil.fr site, the following may be collected: the URL of the links through which the user accessed the covid19.jda-conseil.fr site, the user's access provider, the user's Internet Protocol (IP) address. In any case Covid19 - AMSE Student Dashboard does not collect personal information about the user. In accordance with the provisions of articles 38 and following of law 78-17 of 6 January 1978 relating to data processing, data files and liberties, any user has the right to access, rectify and oppose personal data concerning him or her, by making a written and signed request, accompanied by a copy of the identity document with the signature of the holder of the document, specifying the address to which the reply should be sent. No personal information of the user of the covid19.jda-conseil.fr site is published without the user's knowledge, exchanged, transferred, ceded or sold on any medium whatsoever to third parties. The databases are protected by the provisions of the law of 1 July 1998 transposing directive 96/9 of 11 March 1996 on the legal protection of databases. A page dedicated to the Protection of your Personal Data is available on the Junior Data Analysts website in compliance with the General Data Protection Regulations (RGPD)",
            ]),
        html.H5("8. Applicable law and jurisdiction."),
        html.P([
            "Any dispute in connection with the use of the covid19.jda-conseil.fr site is subject to French law. It is made attribution of exclusive jurisdiction to the competent courts of Paris",
            ]),
        html.H5("9. The main laws concerned."),
        html.P([
            "Law n° 78-87 of January 6, 1978, notably modified by law n° 2004-801 of August 6, 2004 relating to data processing, files and liberties. Law n° 2004-575 of 21 June 2004 for confidence in the digital economy",
            ]),
        html.H5("10. Lexicon."),
        html.P([
            "User: Internet user connecting, using the above-mentioned site. Personal information: 'information that allows, in any form whatsoever, directly or indirectly, the identification of the natural persons to which it applies' (article 4 of the law n° 78-17 of January 6, 1978)",
            ]), 
]


def create_layout(app):
    body = dbc.Container(
        [

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Terms of use"),
                            html.H4("Who are we?"),
                            html.Div(lorem),
                            html.H4("The origin of the project"),
                            html.Div(lorem),
                            html.H4("Data sources"),
                            html.Div(lorem),
                            html.H4("Explanations of the graphs"),
                            html.Div(lorem),
                            html.H4("Acknowledgements"),
                            html.Div(lorem),
                            html.H4("Legal notice"),
                            html.Div(txt_notice),
                        ],
                        style={"text-align":"justify"},
                        xl=12,
                        
                    ),
                ],
                justify="center",
            ),
        ],
        className="mt-4",
    )
                   
    return body