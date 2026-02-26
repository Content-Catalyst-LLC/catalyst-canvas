def aida_fields:
 return ['Attention (hook)', 'Interest (context)', 'Desire (benefit)', 'Action (CTA)']
def heros_journey_fields:
 return ['Call to Adventure', 'Trials', 'Transformation', 'Return with Elixir']
def jtbd_fields:
 return ['Functional Job', 'Emotional Job', 'Social Job', 'Forces: Push', 'Forces: Pull', 'Forces: Anxieties', 'Forces: Habits']
def content_matrix_fields:
 return ['Quadrant: Evergreen/Educational', 'Quadrant: Evergreen/Entertaining', 'Quadrant: Timely/Educational', 'Quadrant: Timely/Entertaining']
def matrix_quadrants:
 return ['Evergreen • Educational', 'Evergreen • Entertaining', 'Timely • Educational', 'Timely • Entertaining']
def get_framework_labels(framework: str):
 f = (framework or 'AIDA').upper
 if f == 'AIDA':
 return 'AIDA', aida_fields
 if f in ('HERO', 'HERO_S_JOURNEY', 'HERO_JOURNEY', 'HERO’S JOURNEY', 'HERO’S', 'HEROS_JOURNEY', 'HERO’S_JOURNEY', 'HJ'):
 return 'Hero’s Journey', heros_journey_fields
 if f == 'JTBD':
 return 'JTBD', jtbd_fields
 if f in ('MATRIX', 'CONTENT_MATRIX', 'CONTENT MATRIX'):
 return 'Content Matrix', content_matrix_fields
 return 'AIDA', aida_fields