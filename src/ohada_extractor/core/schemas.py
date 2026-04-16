"""
OHADA Financial Statement Schemas

Defines account structures and statement configurations for OHADA-compliant
financial statements across 18 African countries.
"""
import logging
from dataclasses import dataclass
from typing import Tuple, List, Optional, Union, Dict
logger = logging.getLogger(__name__)

# Balance Sheet Accounts (29 total)
ASSETS_ACCOUNTS = [
    ('Immobilisations incorporelles', 'AD'),
    ('Frais de développement et de prospection', 'AE'),
    ('Brevets, licences, logiciels et droits similaires', 'AF'),
    ('Fonds commercial et droit au bail', 'AG'),
    ('Autres immobilisations incorporelles', 'AH'),
    ('Immobilisations Corporelles', 'AI'),
    ('Terrains', 'AJ'),
    ('Bâtiments', 'AK'),
    ('Aménagements, agencements et installations', 'AL'),
    ('Matériel, mobilier et actifs biologiques', 'AM'),
    ('Matériel de transport', 'AN'),
    ('Avances et acomptes versés sur immobilisations', 'AP'),
    ('Immobilisations Financières', 'AQ'),
    ('Titres de participation', 'AR'),
    ('Autres immobilisations financières', 'AS'),
    ('Actif Immobilisé', 'AZ'),
    ('Actif circulant HAO', 'BA'),
    ('Stocks et encours', 'BB'),
    ('Créances et emplois assimilés', 'BC'),
    ('Fournisseurs avances versées', 'BH'),
    ('Clients', 'BI'),
    ('Autres créances', 'BJ'),
    ('Actif Circulant', 'BK'),
    ('Titres de placement', 'BQ'),
    ('Valeurs à encaisser', 'BR'),
    ('Banques, chèques postaux, caisse et assimilés', 'BS'),
    ('Trésorerie - Actif', 'BT'),
    ('Écart de conversion - Actif', 'BU'),
    ('Total Actif', 'BZ'),
]

# Liabilities Accounts (28 total)
LIABILITIES_ACCOUNTS = [
    ('Capital', 'CA'),
    ('Apporteurs capital non appelé', 'CB'),
    ('Primes liées au capital social', 'CD'),
    ('Écarts de réévaluation', 'CE'),
    ('Réserves indisponibles', 'CF'),
    ('Réserves libres', 'CG'),
    ('Report à nouveau', 'CH'),
    ('Résultat net de l\'exercice', 'CJ'),
    ('Subventions d\'investissement', 'CL'),
    ('Provisions réglementées', 'CM'),
    ('Capitaux Propres', 'CP'),
    ('Emprunts et dettes financières diverses', 'DA'),
    ('Dettes de location-acquisition', 'DB'),
    ('Provisions pour risques et charges', 'DC'),
    ('Dettes Financières', 'DD'),
    ('Ressources Stables', 'DF'),
    ('Dettes circulantes HAO', 'DH'),
    ('Clients, avances reçues', 'DI'),
    ('Fournisseurs d\'exploitation', 'DJ'),
    ('Dettes fiscales et sociales', 'DK'),
    ('Autres dettes', 'DM'),
    ('Provisions pour risques à court terme', 'DN'),
    ('Dettes Circulantes', 'DP'),
    ('Dettes de location-acquisition à court terme', 'DQ'),
    ('Autres dettes à court terme', 'DR'),
    ('Trésorerie - Passif', 'DT'),
    ('Écart de conversion - Passif', 'DY'),
    ('Total Passif', 'DZ'),
]

# Income Statement Accounts (42 total)
INCOME_ACCOUNTS = [
    ('Ventes de marchandises', 'TA'),
    ('Achats de marchandises', 'RA'),
    ('Variation de stock de marchandises', 'RB'),
    ('Marge commerciale', 'XA'),
    ('Ventes de produits fabriqués', 'TB'),
    ('Travaux et services vendus', 'TC'),
    ('Produits accessoires', 'TD'),
    ('Chiffre d\'affaires', 'XB'),
    ('Produits stockés ou destockage', 'TE'),
    ('Production immobilisée', 'TF'),
    ('Subventions d\'exploitation', 'TG'),
    ('Autres produits', 'TH'),
    ('Transfert de charges d\'exploitation', 'TI'),
    ('Achats de matières premières et fournitures', 'RC'),
    ('Variation de stocks de matières premières', 'RD'),
    ('Autres achats', 'RE'),
    ('Variation de stock d\'autres approvisionnements', 'RF'),
    ('Transports', 'RG'),
    ('Services extérieurs', 'RH'),
    ('Impôts et taxes', 'RI'),
    ('Autres charges', 'RJ'),
    ('Valeur Ajoutée', 'XC'),
    ('Charges de personnel', 'RK'),
    ('Excédent Brut d\'Exploitation', 'XD'),
    ('Reprises d\'amortissements et provisions', 'TJ'),
    ('Dotations aux amortissements et provisions', 'RL'),
    ('Résultat d\'Exploitation', 'XE'),
    ('Revenus financiers et assimilés', 'TK'),
    ('Reprises de provisions financières', 'TL'),
    ('Transfert de charges financières', 'TM'),
    ('Frais financiers et charges assimilées', 'RM'),
    ('Dotations aux provisions financières', 'RN'),
    ('Résultats Financiers', 'XF'),
    ('Résultat des Activités Ordinaires', 'XG'),
    ('Produits et cessions d\'immobilisations', 'TN'),
    ('Autres produits HAO', 'TO'),
    ('Valeurs comptables de cessions d\'immobilisations', 'RO'),
    ('Autres charges HAO', 'RP'),
    ('Résultat Hors Activités Ordinaires', 'XH'),
    ('Participation des travailleurs', 'RQ'),
    ('Impôt sur le résultat', 'RS'),
    ('Résultat Net', 'XI'),
]

# Cash Flow Accounts (25 total)
CASHFLOW_ACCOUNTS = [
    ('Trésorerie nette au 1er janvier', 'ZA'),
    ('Capacité d\'autofinancement', 'FA'),
    ('-Actif circulant HAO', 'FB'),
    ('Variation des stocks', 'FC'),
    ('Variation des créances', 'FD'),
    ('Variation du passif circulant', 'FE'),
    ('Flux opérationnel', 'ZB'),
    ('Acquisitions d\'immobilisations incorporelles', 'FF'),
    ('Acquisitions d\'immobilisations corporelles', 'FG'),
    ('Acquisitions d\'immobilisations financières', 'FH'),
    ('Cessions d\'immobilisations incorporelles', 'FI'),
    ('Cessions d\'immobilisations financières', 'FJ'),
    ('Flux d\'investissement', 'ZC'),
    ('Augmentation de capital', 'FK'),
    ('Subventions d\'investissement', 'FL'),
    ('Prélèvements sur capital', 'FM'),
    ('Dividendes versés', 'FN'),
    ('Flux des capitaux propres', 'ZD'),
    ('Nouveaux emprunts', 'FO'),
    ('Autres financements', 'FP'),
    ('Remboursement emprunts', 'FQ'),
    ('Flux de financement', 'ZE'),
    ('Variation de trésorerie', 'ZF'),
    ('Variation nette de trésorerie', 'ZG'),
    ('Trésorerie nette au 31 décembre', 'ZH'),
]

# Note 31 Accounts (13)
OTHER_ACCOUNTS = [
    ('Capital social','CS'),
    ('Actions ordinaires','AO'),
    ('Actions à dividendes prioritaires (A.D.P) sans droit de vote','ADP'),
    ('Actions nouvelles à émettre','ANE'),
    ('Chiffre d’ffaires hors taxes','CAHT'),
    ('Résultat des activités ordinaires (RAO) hors dotations et reprises (exploitation et financières)','RAO'),
    ('Participation des travailleurs aux bénéfices','PTB'),
    ('Impots sur le résultat','IR'),
    ('Résultat net(4)','RN'),
    ('Résultat distribué(5)','RD'),
    ('Dividende attribués à chaque action','DDA'),
    ('Effectif moyen des travailleurs au cours de l’exercice (6)','EMTE'),
    ('Effectif moyen de personnel extérieur','EMPE')
]

@dataclass
class OHADAStatement:
    """Configuration for an OHADA financial statement type."""
    name: str
    sheet_name: str
    start_account: str
    end_account: str
    account_count: int
    accounts: List[Tuple[str, str]]
    has_value_types: bool  # True for balance sheet (Gross/Amort/Net), False for others
    value_types: Optional[List[str]] = None
    columns_idx: Optional[Tuple[int,...]] = None
    lines_idx: Optional[Tuple[int, ...]] = None

    def __post_init__(self):
        if self.value_types is None:
            self.value_types = ['Brut', 'Amortissement', 'Net'] if self.has_value_types else ['Net']

# OHADA Statement Configurations
OHADA_STATEMENTS = {
    'assets_sheet': OHADAStatement(
        name='Balance Sheet Assets',
        sheet_name='BILAN PAYSAGE',
        start_account='AD',
        end_account='BZ',
        account_count=29,
        accounts=ASSETS_ACCOUNTS,
        has_value_types=True,
        columns_idx = (0, 3, 4, 5, 6),
    ),
    'liabilities_sheet': OHADAStatement(
        name='Balance Sheet Liability',
        sheet_name='BILAN PAYSAGE',
        start_account='CA',
        end_account='DZ',
        account_count=28,
        accounts=LIABILITIES_ACCOUNTS,
        has_value_types=False,
        columns_idx=(0, 3, 4),
    ),
    'income_statement': OHADAStatement(
        name='Income Statement',
        sheet_name='COMPTE DE RESULTAT',
        start_account='TA',
        end_account='XI',
        account_count=42,
        accounts=INCOME_ACCOUNTS,
        has_value_types=False,
        columns_idx=(0, 4, 5)
    ),
    'cashflow': OHADAStatement(
        name='Cash Flow Statement',
        sheet_name='TABLEAU DES FLUX DE TRESORERIE',
        start_account='ZA',
        end_account='ZH',
        account_count=25,
        accounts=CASHFLOW_ACCOUNTS,
        has_value_types=False,
        columns_idx= (0, 4, 5),
    ),
    'other_last_years': OHADAStatement(
        name='Other Characteristics',
        sheet_name='NOTE 31',
        start_account='Capital social',
        end_account='Effectif moyen de personnel extérieur',
        account_count=18,
        accounts=OTHER_ACCOUNTS,
        has_value_types=False,
        columns_idx=(0, 1, 2),
        lines_idx=(0, 1, 2, 3, 7, 8, 9, 10, 11, 13, 14, 16, 17)
    ),
}

@dataclass
class OHADANoteStatement:
    """Configuration for an OHADA note (annex) extraction."""
    sheet_name: str
    start_marker: str
    end_marker: str
    expected_rows: int
    columns_idx: Optional[Tuple[int, ...]]
    lines_idx: Optional[Tuple[int, ...]]
    keys: Union[str, Tuple[str, ...]]   # e.g. 'note3a' or ('fiche2_a','fiche2_b')
    names: Union[str, Tuple[str, ...]]  # human-readable names
    is_special: bool = False            # NOTE 5, NOTE 30, Fiche R2
    preprocess_rules: Optional[Dict] = None  # rules for preprocess_data

OHADA_NOTES = {

    # ---------------------------------------------------------
    # SPECIAL SHEETS (custom preprocessing)
    # ---------------------------------------------------------

    'Fiche R2': OHADANoteStatement(
        sheet_name='Fiche R2',
        start_marker='ZK',
        end_marker='Divers',
        expected_rows=15,
        columns_idx=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15),
        lines_idx=None,
        keys=('ficher2_a', 'ficher2_b'),
        names=('IDENTIFICATION', 'REVENU BREAKDOWN'),
        is_special=True
    ),

    'NOTE 5': OHADANoteStatement(
        sheet_name='NOTE 5',
        start_marker='Libellés',
        end_marker='TOTAL',
        expected_rows=30,
        columns_idx=None,
        lines_idx=None,
        keys='note5',
        names='ACTIF CIRCULANT HAO',
        is_special=True,
        preprocess_rules={
            'columns': [1, 2],
            'refs': [
                "Créances sur cessions d'immobilisations",
                "Fournisseurs d'investissements",
                "Fournisseurs d'investissements effets à payer"
            ]
        }
    ),

    'NOTE 30': OHADANoteStatement(
        sheet_name='NOTE 30',
        start_marker='Libellés',
        end_marker='TOTAL',
        expected_rows=30,
        columns_idx=None,
        lines_idx=None,
        keys='note30',
        names='AUTRES CHARGES ET PRODUITS HAO',
        is_special=True,
        preprocess_rules={
            'columns': [1, 2],
            'refs': [
                'Charges provisionnées HAO',
                'Dotations hors activités ordinaires',
                'Reprise des charges pour dépréciations et provisions à court terme HAO ',
                'Reprises hors activités ordinaire'
            ]
        }
    ),

    # ---------------------------------------------------------
    # STANDARD NOTES (raw + preprocessed)
    # ---------------------------------------------------------

    'NOTE 3A': OHADANoteStatement(
        sheet_name='NOTE 3A',
        start_marker='IMMOBILISATIONS INCORPORELLES',
        end_marker='TOTAL GENERAL',
        expected_rows=20,
        columns_idx=(4, 5),
        lines_idx=(0, 5, 14, 15, 16),
        keys='note3a',
        names='IMMOBILISATION BRUTE'
    ),

    'NOTE 3B': OHADANoteStatement(
        sheet_name='NOTE 3B',
        start_marker='Brevets, licences, logiciels et droits similaires',
        end_marker='TOTAL GENERAL',
        expected_rows=11,
        columns_idx=(5, 6),
        lines_idx=(3, 9),
        keys='note3b',
        names='BIENS PRIS EN LOCATION ACQUISITION'
    ),

    'NOTE 3C': OHADANoteStatement(
        sheet_name='NOTE 3C',
        start_marker='Frais de développement et de prospection',
        end_marker='TOTAL GENERAL',
        expected_rows=14,
        columns_idx=(2, 3),
        lines_idx=(4, 12),
        keys='note3c',
        names='IMMOBILISATION AMORTISSEMENT'
    ),

    'NOTE 3D': OHADANoteStatement(
        sheet_name='NOTE 3D',
        start_marker='Frais de développement et de prospection',
        end_marker='TOTAL GENERAL',
        expected_rows=15,
        columns_idx=(4, 5),
        lines_idx=(4, 10, 13),
        keys='note3d',
        names='IMMOBILISATION : PLUS-VALUES ET MOINS VALUE DE CESSION'
    ),

    'NOTE 3F': OHADANoteStatement(
        sheet_name='NOTE 3F',
        start_marker='Libellés',
        end_marker='TOTAL GENERAL',
        expected_rows=10,
        columns_idx=(2, 4, 6),
        lines_idx=(0, 3, 4, 5, 6),
        keys='note3f',
        names='TABLEAU D’ÉTALEMENT DES CHARGES IMMOBILISEES'
    ),

    'NOTE 4': OHADANoteStatement(
        sheet_name='NOTE 4',
        start_marker='Libelés',
        end_marker='TOTAL NET DE DEPRECIATION',
        expected_rows=12,
        columns_idx=(1, 2, 4),
        lines_idx=(7, 8, 9, 10),
        keys='note4',
        names='IMMOBILISATION FINANCIÈRE'
    ),

    'NOTE 6': OHADANoteStatement(
        sheet_name='NOTE 6',
        start_marker='Libelés',
        end_marker='TOTAL NET DE DEPRECIATION',
        expected_rows=12,
        columns_idx=(0, 1, 2),
        lines_idx=(9, 10),
        keys='note6',
        names='STOCK ET ENCOURS'
    ),

    'NOTE 7': OHADANoteStatement(
        sheet_name='NOTE 7',
        start_marker='Libelés',
        end_marker='TOTAL CLIENTS CREDITEURS',
        expected_rows=16,
        columns_idx=(1, 2, 4),
        lines_idx=(5, 9, 10, 15),
        keys='note7',
        names='CLIENTS'
    ),

    'NOTE 8': OHADANoteStatement(
        sheet_name='NOTE 8',
        start_marker='Libellés',
        end_marker='TOTAL NET DE DEPRECIATION',
        expected_rows=14,
        columns_idx=(1, 2, 4),
        lines_idx=(11, 12),
        keys='note8',
        names='AUTRES CREANCES'
    ),

    'NOTE 9': OHADANoteStatement(
        sheet_name='NOTE 9',
        start_marker='Libellés',
        end_marker='TOTAL NET DE DEPRECIATION',
        expected_rows=11,
        columns_idx=(1, 2),
        lines_idx=(8, 9),
        keys='note9',
        names='TITRE DE PLACEMENT'
    ),

    'NOTE 10': OHADANoteStatement(
        sheet_name='NOTE 10',
        start_marker='Libellés',
        end_marker='TOTAL NET DE DEPRECIATION',
        expected_rows=10,
        columns_idx=(1, 2),
        lines_idx=(7, 8),
        keys='note10',
        names='VALEUR A ENCAISSER'
    ),

    'NOTE 11': OHADANoteStatement(
        sheet_name='NOTE 11',
        start_marker='Libellés',
        end_marker='TOTAL NET DE DEPRECIATION',
        expected_rows=16,
        columns_idx=(1, 2),
        lines_idx=(13, 14),
        keys='note11',
        names='DISPONIBILITES'
    ),

    'NOTE 16A': OHADANoteStatement(
        sheet_name='NOTE 16A',
        start_marker='Emprunts obligatoires',
        end_marker='TOTAL PROVISIONS POUR RISQUES ET CHARGES',
        expected_rows=31,
        columns_idx=(1, 2, 5),
        lines_idx=(5, 10, 14, 16, 30),
        keys='note16',
        names='DETTES FINANCIERES ET RESSOURCES ASSIMILEES'
    ),

    'NOTE 17': OHADANoteStatement(
        sheet_name='NOTE 17',
        start_marker='Libellés',
        end_marker='TOTAL FOURNISSEURS DEBITEURS',
        expected_rows=11,
        columns_idx=(5, 6),
        lines_idx=(6, 10),
        keys='note17',
        names='FOURNISSEURS DEXPLOITATION'
    ),

    'NOTE 18': OHADANoteStatement(
        sheet_name='NOTE 18',
        start_marker='libellés',
        end_marker='TOTAL DETTES SOCIALES ET FISCALES',
        expected_rows=15,
        columns_idx=(6, 7),
        lines_idx=(7, 13),
        keys='note18',
        names='DETTES FISCALES ET SOCIALES'
    ),

    'NOTE 19': OHADANoteStatement(
        sheet_name='NOTE 19',
        start_marker='Libellés',
        end_marker='TOTAL AUTRES DETTES',
        expected_rows=21,
        columns_idx=(1, 2, 5),
        lines_idx=(6, 7),
        keys='note19',
        names='AUTRES DETTES ET PROVISIONS POUR RISQUES A COURT TERME'
    ),

    'NOTE 28': OHADANoteStatement(
        sheet_name='NOTE 28',
        start_marker='1. Provisions réglementées',
        end_marker='TOTAL PROVISIONS ET DEPRECIATIONS',
        expected_rows=17,
        columns_idx=(2, 3, 4, 5, 6, 7),
        lines_idx=(1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12),
        keys='note28',
        names='PROVISIONS ET DEPRECIATIONS INSCRITES AU BILAN'
    ),

    'NOTE 29': OHADANoteStatement(
        sheet_name='NOTE 29',
        start_marker='Libellés',
        end_marker='TOTAL',
        expected_rows=22,
        columns_idx=(1, 2),
        lines_idx=(1, 2, 4),
        keys='note29',
        names='CHARGES ET REVENUS FINANCIERS'
    ),
}

# ----------------------------------------------------------------------
#  STATIC REFERENCE TABLES
# ----------------------------------------------------------------------

LEGAL_FORMS = [
    (0, "Société Anonyme (SA) à participation Pays OHADA"),
    (1, "Société Anonyme (SA)"),
    (2, "Société à Responsabilité Limitée (SARL)"),
    (3, "Société en Commandite Simple (SCS)"),
    (4, "Société en Nom Collectif (SNC)"),
    (5, "Société en Participation (SP)"),
    (6, "Groupement d'Intérêt économique (GIE)"),
    (7, "Association"),
    (8, "Société par Actions Simplifiée (SAS)"),
    (9, "Autre forme juridique (à préciser)")
]

SIEGE_SOCIAL = [
    (1, "Bénin"), (2, "Burkina"), (3, "Côte d'Ivoire"), (4, "Guinée Bissau"),
    (5, "Mali"), (6, "Niger"), (7, "Sénégal"), (8, "Togo"),
    (9, "Cameroun"), (10, "Congo"), (11, "Gabon"), (12, "République Centrafricaine"),
    (13, "Tchad"), (14, "Comores"), (15, "Guinée"), (16, "Guinée Équatoriale"),
    (17, "Congo RDC"), (21, "Autres pays africains"), (23, "France"),
    (39, "Autres pays de l'Union Européenne"), (40, "USA"), (41, "Canada"),
    (49, "Autres pays américains"), (50, "Pays Asiatiques"), (99, "Autres pays")
]

CODES_FISCAUX = [
    (1, "Réel normal"),
    (2, "Réel simplifié"),
    (3, "Synthétique"),
    (4, "Forfait")
]

CURRENCY_MAPPING = {
    1: "XOF", 2: "XOF", 3: "XOF", 4: "XOF", 5: "XOF",
    6: "XOF", 7: "XOF", 8: "XOF",
    9: "XAF", 10: "XAF", 11: "XAF", 12: "XAF", 13: "XAF", 16: "XAF",
    14: "KMF",
    15: "GNF"
}

# ----------------------------------------------------------------------
#  MAPPING HELPERS (FINAL VERSION)
# ----------------------------------------------------------------------

def _safe_int(code: str) -> Optional[int]:
    """Convert a code to int safely."""
    try:
        return int(code)
    except (ValueError, TypeError):
        logger.error(f" Invalid code '{code}' (not an integer)")
        return None


def fetch_legal_form(code: str, legal_forms: List[Tuple[int, str]]) -> Optional[str]:
    """Return the legal form label for a given code."""
    code_int = _safe_int(code)
    if code_int is None:
        return None

    for form_code, label in legal_forms:
        if form_code == code_int:
            return label

    logger.error(f" Unknown legal form code '{code_int}'. Valid: {legal_forms}")
    return None


def fetch_headquarter_country(code: str, country_list: List[Tuple[int, str]]) -> Optional[str]:
    """Return the country name for a given headquarters code."""
    code_int = _safe_int(code)
    if code_int is None:
        return None

    for country_code, name in country_list:
        if country_code == code_int:
            return name

    logger.error(f" Unknown country code '{code_int}'. Valid: {country_list}")
    return None


def fetch_currency(code: str) -> Optional[str]:
    """Return the currency associated with the country code."""
    code_int = _safe_int(code)
    if code_int is None:
        return None

    currency = CURRENCY_MAPPING.get(code_int)
    if currency:
        return currency

    logger.error(
        f"Unknown currency code '{code_int}'. "
        f"Valid currencies: {set(CURRENCY_MAPPING.values())}"
    )
    return None


def fetch_regime_fiscal(code: str, regime_fiscaux: List[Tuple[int, str]]) -> Optional[str]:
    """Return the fiscal regime label for a given code."""
    code_int = _safe_int(code)
    if code_int is None:
        return None

    for regime_code, label in regime_fiscaux:
        if regime_code == code_int:
            return label

    logger.error(f" Unknown fiscal regime code '{code_int}'. Valid: {regime_fiscaux}")
    return None