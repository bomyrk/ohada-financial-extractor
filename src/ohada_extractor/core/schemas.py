"""
OHADA Financial Statement Schemas

Defines account structures and statement configurations for OHADA-compliant
financial statements across 18 African countries.
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional

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
    ('Trésorerie - Passif', 'DS'),
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
    ('Variation des stocks', 'FB'),
    ('Variation des créances', 'FC'),
    ('Variation du passif circulant', 'FD'),
    ('Flux opérationnel', 'ZB'),
    ('Acquisitions d\'immobilisations incorporelles', 'FE'),
    ('Acquisitions d\'immobilisations corporelles', 'FF'),
    ('Acquisitions d\'immobilisations financières', 'FG'),
    ('Cessions d\'immobilisations incorporelles', 'FH'),
    ('Cessions d\'immobilisations financières', 'FI'),
    ('Flux d\'investissement', 'ZC'),
    ('Augmentation de capital', 'FJ'),
    ('Subventions d\'investissement', 'FK'),
    ('Prélèvements sur capital', 'FL'),
    ('Dividendes versés', 'FM'),
    ('Flux des capitaux propres', 'ZD'),
    ('Nouveaux emprunts', 'FN'),
    ('Autres financements', 'FO'),
    ('Remboursement emprunts', 'FP'),
    ('Flux de financement', 'ZE'),
    ('Variation de trésorerie', 'ZF'),
    ('Variation nette de trésorerie', 'ZG'),
    ('Trésorerie nette au 31 décembre', 'ZH'),
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
}