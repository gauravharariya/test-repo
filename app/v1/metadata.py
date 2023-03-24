from app import db
from app.common.blueprint import EnhancedBlueprint
from app.common.controllers import BaseMethodView
from app.models import PipelineTask
from app.schema import pipeline_task_schema, PipelineTaskSchema

blp = EnhancedBlueprint("metadata", __name__)


@blp.route("/pipeline-tasks", tags=["pipeline-task"])
class PipelineTaskCreate(BaseMethodView):
    @blp.arguments(pipeline_task_schema)
    @blp.response(200, pipeline_task_schema)
    def post(self, data):
        item = PipelineTask(**data)
        db.session.add(item)
        db.session.commit()
        return item


@blp.route("/pipeline-tasks/<int:pipeline_task_id>", tags=["pipeline-task"])
class PipelineTaskGetUpdate(BaseMethodView):
    @blp.response(200, pipeline_task_schema)
    def get(self, pipeline_task_id):
        """Get Pipeline task by id"""
        return PipelineTask.query.get_or_404(pipeline_task_id)

    @blp.arguments(PipelineTaskSchema(partial=True))
    @blp.response(200, pipeline_task_schema)
    def patch(self, data, pipeline_task_id):
        """Update Pipeline task"""
        # get task by id
        item = PipelineTask.query.get_or_404(pipeline_task_id)

        # update on task instance
        for attr, value in data.items():
            if hasattr(item, attr):
                setattr(item, attr, value)
        # save updated instance to db
        db.session.add(item)
        db.session.commit()
        return item
