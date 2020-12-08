argos
-----.

ou-addons est un sous-module de module argos.
Pour récupérer les sources, exécuter ces commandes après le clonning de repository 

+ git submodule init
+ git submodule update 

ce projet utilise le mécanisme de job queue pour synchroniser le lancement des crons.
pour le paramétrer, ajouter les lignes suivantes dans le fichier config d'odoo :

[options]

(...)

server_wide_modules = queue_job

(...)

[queue_job]

channels = root:1