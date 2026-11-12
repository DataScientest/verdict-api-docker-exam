"""Génère data/references.json : les exemples de référence annotés.

180 avis clients fictifs, 60 par intention (positif, negatif, neutre), répartis
sur six domaines pour que le classement repose sur le ton de l'avis et non sur
le vocabulaire d'un secteur. Les avis neutres sont factuels : ils décrivent
sans juger.

Lancer depuis la racine du dépôt : python scripts/gen_references.py
"""

from __future__ import annotations

import json
from pathlib import Path

REFERENCES: dict[str, dict[str, list[str]]] = {
    "hotel": {
        "positif": [
            "Chambre impeccable et literie très confortable, nous avons parfaitement dormi.",
            "Le personnel de la réception a été adorable du début à la fin du séjour.",
            "Petit-déjeuner copieux et varié, un vrai régal chaque matin.",
            "Vue magnifique depuis le balcon, nous reviendrons sans hésiter.",
            "Accueil chaleureux, on s'est tout de suite senti attendus.",
            "Un séjour parfait, je recommande cet hôtel à tous mes proches.",
            "La piscine était propre et le spa vraiment relaxant, quel bonheur.",
            "Excellent rapport qualité-prix, bien au-delà de nos attentes.",
            "Le concierge nous a donné des conseils précieux, merci infiniment.",
            "Calme absolu la nuit, une parenthèse reposante très appréciée.",
        ],
        "negatif": [
            "Chambre sale, cheveux dans la douche et draps tachés, inadmissible.",
            "Le personnel de la réception était désagréable et méprisant.",
            "Bruit insupportable toute la nuit, impossible de fermer l'œil.",
            "Climatisation en panne pendant trois jours malgré nos plaintes.",
            "Hôtel très décevant, rien ne correspond aux photos du site.",
            "Petit-déjeuner pauvre et froid, une honte à ce prix.",
            "On nous a facturé des frais cachés au moment du départ, scandaleux.",
            "Moisissures dans la salle de bain, je déconseille fortement.",
            "Réservation perdue à notre arrivée et aucune solution proposée.",
            "Le pire séjour de ma vie, à fuir absolument.",
        ],
        "neutre": [
            "L'hôtel se trouve à dix minutes à pied de la gare centrale.",
            "La chambre est située au troisième étage, avec ascenseur.",
            "Le petit-déjeuner est servi de 7 heures à 10 heures.",
            "Nous avons réservé une chambre double pour deux nuits en mai.",
            "Le parking de l'hôtel est payant et compte une vingtaine de places.",
            "L'arrivée se fait à partir de 15 heures et le départ avant 11 heures.",
            "L'établissement dispose d'une piscine extérieure et d'une salle de sport.",
            "La chambre comporte un lit double, un bureau et une salle d'eau.",
            "Le wifi est inclus dans le prix de la nuitée.",
            "L'hôtel compte quarante chambres réparties sur quatre étages.",
        ],
    },
    "restaurant": {
        "positif": [
            "Des plats savoureux et généreux, le chef a un vrai talent.",
            "Service attentionné et souriant, une soirée délicieuse.",
            "Le dessert était divin, je m'en souviendrai longtemps.",
            "Produits frais et cuisine inventive, une très belle découverte.",
            "Cadre charmant et ambiance agréable, nous avons passé un super moment.",
            "La meilleure pizza que j'ai mangée depuis des années.",
            "Carte des vins excellente et conseils du sommelier parfaits.",
            "Tout était délicieux, de l'entrée au café, bravo à l'équipe.",
            "Accueil adorable avec les enfants, merci pour votre patience.",
            "Un restaurant qui mérite largement sa réputation, je recommande.",
        ],
        "negatif": [
            "Plat froid, viande trop cuite et sauce sans aucun goût.",
            "Une heure d'attente pour être servis, serveur introuvable.",
            "Addition exorbitante pour des portions ridicules, arnaque totale.",
            "J'ai été malade toute la nuit après ce repas, honteux.",
            "Serveur grossier qui a levé les yeux au ciel à chaque question.",
            "Table sale et couverts douteux, l'hygiène laisse à désirer.",
            "On nous a servi le mauvais plat et refusé de le changer.",
            "Cuisine industrielle réchauffée au micro-ondes, très déçu.",
            "Musique beaucoup trop forte, impossible de discuter.",
            "Plus jamais dans ce restaurant, une expérience lamentable.",
        ],
        "neutre": [
            "Le restaurant est fermé le dimanche soir et le lundi.",
            "Nous étions quatre et avons réservé une table pour 20 heures.",
            "La carte propose trois entrées, cinq plats et quatre desserts.",
            "Le menu du midi est servi en semaine uniquement.",
            "La salle compte environ cinquante couverts et une terrasse.",
            "Le restaurant se situe au rez-de-chaussée d'un immeuble ancien.",
            "Les réservations se font par téléphone ou sur le site internet.",
            "Nous avons commandé deux plats du jour et une carafe d'eau.",
            "Le paiement par carte est accepté à partir de dix euros.",
            "La cuisine reste ouverte jusqu'à 22 heures en semaine.",
        ],
    },
    "livraison": {
        "positif": [
            "Colis livré en avance et parfaitement emballé, top.",
            "Le livreur a été très aimable et a pris soin du paquet.",
            "Suivi précis du début à la fin, livraison sans aucun souci.",
            "Reçu le lendemain de la commande, une rapidité impressionnante.",
            "Livraison soignée au pied de ma porte, rien à redire.",
            "Le transporteur m'a prévenu de son arrivée, très pratique.",
            "Emballage écologique et solide, j'ai beaucoup apprécié.",
            "Livraison gratuite et rapide, un service vraiment au top.",
            "Le livreur a attendu que je descende, quelle gentillesse.",
            "Tout est arrivé en parfait état, merci pour ce sérieux.",
        ],
        "negatif": [
            "Colis jamais reçu alors qu'il est indiqué comme livré.",
            "Carton éventré et produit cassé à l'arrivée, inacceptable.",
            "Trois semaines de retard sans la moindre explication.",
            "Le livreur a jeté le paquet par-dessus le portail.",
            "Avis de passage déposé alors que j'étais bien chez moi.",
            "Suivi bloqué depuis dix jours, personne ne répond.",
            "Livraison déposée chez un voisin inconnu, colis introuvable.",
            "Frais de livraison exorbitants pour un délai catastrophique.",
            "Le transporteur a perdu ma commande et refuse de rembourser.",
            "Service de livraison lamentable, je ne commanderai plus.",
        ],
        "neutre": [
            "Le colis a été remis au point relais situé près de chez moi.",
            "La livraison est prévue entre trois et cinq jours ouvrés.",
            "J'ai choisi la livraison standard lors de la commande.",
            "Le numéro de suivi a été envoyé par courriel le jour de l'expédition.",
            "Le transporteur livre du lundi au samedi.",
            "Le paquet pesait environ deux kilos.",
            "La commande a été expédiée depuis l'entrepôt de Lyon.",
            "Une signature est demandée à la remise du colis.",
            "Le colis contenait deux articles et une facture.",
            "La livraison a eu lieu mardi en fin d'après-midi.",
        ],
    },
    "produit": {
        "positif": [
            "Produit de grande qualité, solide et très bien fini.",
            "Exactement conforme à la description, je suis ravi.",
            "Batterie qui tient très longtemps, une excellente surprise.",
            "Très facile à utiliser, même pour un débutant, bravo.",
            "Le tissu est doux et la taille parfaite, je recommande.",
            "Un achat que je ne regrette pas du tout, super produit.",
            "Silencieux et efficace, il fait parfaitement son travail.",
            "Design élégant et matériaux haut de gamme, j'adore.",
            "Rapport qualité-prix imbattable, foncez.",
            "Mon fils est enchanté de ce cadeau, merci.",
        ],
        "negatif": [
            "Produit tombé en panne au bout de deux jours.",
            "Rien à voir avec la photo, couleur et matière décevantes.",
            "Fabrication de mauvaise qualité, tout s'est cassé rapidement.",
            "Notice incompréhensible et pièce manquante dans la boîte.",
            "Taille beaucoup trop petite et tissu qui gratte, à éviter.",
            "Bruit horrible au démarrage, totalement inutilisable.",
            "La batterie ne tient même pas une heure, une arnaque.",
            "Odeur chimique très forte à l'ouverture, inquiétant.",
            "Je regrette vraiment cet achat, argent jeté par la fenêtre.",
            "Produit défectueux dès la première utilisation, très déçu.",
        ],
        "neutre": [
            "J'ai commandé ce modèle en taille M et en coloris bleu.",
            "L'appareil fonctionne sur secteur et sur batterie.",
            "La boîte contient le produit, un câble et une notice.",
            "Le produit mesure trente centimètres de haut.",
            "Il existe en trois coloris différents sur le site.",
            "L'article est garanti deux ans par le fabricant.",
            "Le montage nécessite un tournevis cruciforme.",
            "Le produit pèse un peu moins d'un kilo.",
            "La notice est disponible en français et en anglais.",
            "Je l'utilise principalement le week-end.",
        ],
    },
    "service_client": {
        "positif": [
            "Conseillère très patiente qui a résolu mon problème en cinq minutes.",
            "Réponse rapide et claire à ma réclamation, merci beaucoup.",
            "Remboursement effectué sans discussion, un service exemplaire.",
            "Enfin un service client à l'écoute et vraiment efficace.",
            "Le technicien a été compétent et très pédagogue.",
            "Échange accepté immédiatement, une expérience très positive.",
            "Équipe disponible et souriante, je suis conquis.",
            "Mon dossier a été traité avec beaucoup de professionnalisme.",
            "On m'a rappelé comme promis, c'est rare et appréciable.",
            "Un geste commercial généreux après un petit souci, bravo.",
        ],
        "negatif": [
            "Quarante minutes d'attente au téléphone pour rien.",
            "Conseiller impoli qui m'a raccroché au nez.",
            "Aucune réponse à mes cinq courriels, c'est honteux.",
            "On me renvoie de service en service sans solution.",
            "Remboursement promis depuis deux mois et toujours rien.",
            "Le chatbot tourne en boucle, impossible de parler à un humain.",
            "Ils ont refusé la garantie sous un prétexte ridicule.",
            "Service client inexistant, je suis furieux.",
            "On m'a menti sur les délais de traitement de mon dossier.",
            "Expérience désastreuse, je résilie mon abonnement.",
        ],
        "neutre": [
            "J'ai contacté le service client par téléphone jeudi matin.",
            "Le service client est joignable du lundi au vendredi de 9 h à 18 h.",
            "Ma demande porte le numéro de dossier 48213.",
            "J'ai envoyé une photo du produit en pièce jointe.",
            "Le formulaire de contact se trouve en bas de la page d'accueil.",
            "On m'a demandé mon numéro de commande et ma date d'achat.",
            "La procédure de retour se fait en ligne depuis l'espace client.",
            "J'ai reçu un accusé de réception automatique par courriel.",
            "Le conseiller m'a transféré vers le service technique.",
            "Le délai de traitement annoncé est de dix jours ouvrés.",
        ],
    },
    "transport": {
        "positif": [
            "Train parfaitement à l'heure et voiture très propre.",
            "Chauffeur prudent et sympathique, trajet très agréable.",
            "Sièges confortables et wifi efficace, j'ai pu travailler.",
            "Le contrôleur a été très arrangeant avec mon billet, merci.",
            "Vol sans turbulence et équipage aux petits soins.",
            "Correspondance assurée malgré un léger retard, bien joué.",
            "Application de réservation simple et rapide, j'adore.",
            "Le bus était neuf, climatisé et très ponctuel.",
            "Embarquement fluide et personnel accueillant, parfait.",
            "Un trajet reposant, je reprendrai cette compagnie.",
        ],
        "negatif": [
            "Train supprimé au dernier moment sans aucune information.",
            "Deux heures de retard et pas un mot d'excuse.",
            "Bagage perdu et aucune nouvelle depuis une semaine.",
            "Chauffeur agressif qui conduisait beaucoup trop vite.",
            "Toilettes hors service et wagon sale, voyage pénible.",
            "Vol annulé et aucune solution de relogement proposée.",
            "Climatisation en panne en plein été, insupportable.",
            "Surbooking : on m'a refusé l'embarquement malgré mon billet.",
            "Le bus n'est jamais passé à l'arrêt, j'ai raté mon rendez-vous.",
            "Compagnie à éviter, une organisation lamentable.",
        ],
        "neutre": [
            "Le train part de la gare de Lyon à 8 h 12.",
            "Le trajet dure environ deux heures et demie.",
            "J'avais réservé une place côté fenêtre en seconde classe.",
            "Le bus dessert douze arrêts entre le centre et l'aéroport.",
            "Un bagage cabine est inclus dans le tarif de base.",
            "L'embarquement ferme vingt minutes avant le départ.",
            "Le vol fait une escale à Francfort.",
            "Les billets sont échangeables jusqu'à la veille du départ.",
            "La ligne fonctionne de 6 heures à minuit en semaine.",
            "Nous avons voyagé à deux avec une valise chacun.",
        ],
    },
}


def build() -> list[dict]:
    references = []
    next_id = 1
    for domain, by_label in REFERENCES.items():
        for label, texts in by_label.items():
            for text in texts:
                references.append(
                    {"id": next_id, "text": text, "label": label, "domain": domain}
                )
                next_id += 1
    return references


if __name__ == "__main__":
    data = build()
    out = Path("data/references.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(data)} exemples écrits dans {out}")
