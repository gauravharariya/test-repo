## Creating Migration
Overtime changes needed to the models need to be managed, that could be managed via Alembic.

You can then generate new migration after model changes:
```shell
flask db migrate -m "name_of_migration"
```
The migration script needs to be reviewed and edited, as Alembic is not always able to detect every change you make to your models.

Then you can apply the changes described by the migration script to your database:
```shell
flask db upgrade
```
Each time the database models change, repeat the migrate and upgrade commands.

To sync the database in another system just refresh the migrations folder from source control and run the upgrade command.
