# Generated by Django 5.0.6 on 2024-06-15 12:47

import backend.storage
import backend.tools.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tasks", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Content",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField()),
                ("usage_count", models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="ProjectAssistant",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("assistant_name", models.CharField(max_length=32)),
                ("step", models.CharField(max_length=32)),
                ("statistics", models.JSONField(default=dict)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "task",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="tasks.task",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                (
                    "default_syntax",
                    models.CharField(
                        max_length=32,
                        validators=[backend.tools.validators.identifier_validator],
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "editors",
                    models.ManyToManyField(
                        related_name="edited_models", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owned_models",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task_runner",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tasks.taskrunner",
                    ),
                ),
            ],
            options={
                "verbose_name": "Project",
                "verbose_name_plural": "Projects",
            },
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "path",
                    models.CharField(
                        max_length=250,
                        validators=[backend.tools.validators.path_validator],
                    ),
                ),
                ("encoding", models.CharField(default="utf-8", max_length=16)),
                (
                    "line_endings",
                    models.CharField(
                        choices=[("lf", "LF"), ("crlf", "CR/LF")],
                        default="lf",
                        max_length=4,
                    ),
                ),
                ("is_preview", models.BooleanField(default=False)),
                (
                    "document_syntax",
                    models.CharField(
                        max_length=32,
                        null=True,
                        validators=[backend.tools.validators.identifier_validator],
                    ),
                ),
                ("minimum_fragment_size", models.PositiveBigIntegerField(null=True)),
                ("maximum_fragment_size", models.PositiveBigIntegerField(null=True)),
                (
                    "size_unit",
                    models.CharField(
                        max_length=32,
                        null=True,
                        validators=[backend.tools.validators.identifier_validator],
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "predecessor",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="successors",
                        to="backend.document",
                    ),
                ),
            ],
            options={
                "verbose_name": "Document",
                "verbose_name_plural": "Documents",
            },
        ),
        migrations.CreateModel(
            name="EgressAssistant",
            fields=[
                (
                    "projectassistant_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="backend.projectassistant",
                    ),
                ),
                (
                    "destination",
                    models.CharField(
                        max_length=32,
                        validators=[
                            backend.tools.validators.egress_destination_validator
                        ],
                    ),
                ),
                ("working_directory", models.CharField(blank=True, max_length=250)),
            ],
            options={
                "verbose_name": "Egress",
            },
            bases=("backend.projectassistant",),
        ),
        migrations.CreateModel(
            name="IngestAssistant",
            fields=[
                (
                    "projectassistant_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="backend.projectassistant",
                    ),
                ),
                (
                    "uploaded_file",
                    models.FileField(
                        storage=backend.storage.BackendWorkingStorage(),
                        upload_to="uploads/",
                    ),
                ),
                (
                    "minimum_fragment_size",
                    models.PositiveBigIntegerField(
                        default=0, verbose_name="Minimum Fragment Size"
                    ),
                ),
                (
                    "maximum_fragment_size",
                    models.PositiveBigIntegerField(
                        default=1024, verbose_name="Maximum Fragment Size"
                    ),
                ),
                (
                    "size_unit",
                    models.CharField(
                        max_length=32,
                        validators=[backend.tools.validators.identifier_validator],
                    ),
                ),
                ("working_directory", models.CharField(blank=True, max_length=250)),
            ],
            options={
                "verbose_name": "Ingest",
            },
            bases=("backend.projectassistant",),
        ),
        migrations.CreateModel(
            name="RevisionAssistant",
            fields=[
                (
                    "projectassistant_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="backend.projectassistant",
                    ),
                ),
                (
                    "revision_label",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        validators=[backend.tools.validators.name_validator],
                        verbose_name="Revision Label",
                    ),
                ),
                (
                    "keep_fragments",
                    models.BooleanField(
                        default=False,
                        verbose_name="Keep all split points from the selected version.",
                    ),
                ),
                (
                    "copy_review",
                    models.BooleanField(
                        default=False,
                        verbose_name="Copy all review states into the new revision",
                    ),
                ),
            ],
            options={
                "verbose_name": "New Revision Assistant",
                "verbose_name_plural": "New Revision Assistants",
            },
            bases=("backend.projectassistant",),
        ),
        migrations.CreateModel(
            name="TransformationAssistant",
            fields=[
                (
                    "projectassistant_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="backend.projectassistant",
                    ),
                ),
                (
                    "transformed_states",
                    models.IntegerField(
                        choices=[
                            (0, "Transform only fragments with no transformations"),
                            (
                                1,
                                "Transform fragments with errors or no transformations",
                            ),
                            (
                                2,
                                "Transform all fragments, except ones with manual edits",
                            ),
                            (3, "Transform all fragments"),
                        ],
                        default=0,
                    ),
                ),
                ("review_unprocessed", models.BooleanField(default=True)),
                ("review_pending", models.BooleanField(default=False)),
                ("review_approved", models.BooleanField(default=False)),
                ("review_rejected", models.BooleanField(default=True)),
                ("auto_approve_unchanged", models.BooleanField(default=True)),
                (
                    "stop_consecutive_failures",
                    models.PositiveSmallIntegerField(default=10),
                ),
                ("stop_total_failures", models.PositiveSmallIntegerField(default=0)),
                ("rollback_on_failure", models.BooleanField(default=True)),
                ("failure_reason", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Transformation Assistant",
                "verbose_name_plural": "Transformation Assistants",
            },
            bases=("backend.projectassistant",),
        ),
        migrations.CreateModel(
            name="Fragment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("position", models.IntegerField()),
                ("first_line_number", models.PositiveIntegerField(null=True)),
                ("size", models.BigIntegerField()),
                ("size_bytes", models.BigIntegerField()),
                ("size_characters", models.BigIntegerField()),
                ("size_words", models.BigIntegerField()),
                ("size_lines", models.BigIntegerField()),
                (
                    "review_state",
                    models.SmallIntegerField(
                        choices=[
                            (0, "Unprocessed"),
                            (1, "Pending"),
                            (2, "Approved"),
                            (3, "Rejected"),
                        ],
                        default=0,
                    ),
                ),
                ("has_text_changes", models.BooleanField(default=False)),
                ("context", models.JSONField(null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "content",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="backend.content",
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fragments",
                        to="backend.document",
                    ),
                ),
            ],
            options={
                "verbose_name": "Document Fragment",
                "verbose_name_plural": "Document Fragments",
            },
        ),
        migrations.CreateModel(
            name="LearningSet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=200,
                        validators=[backend.tools.validators.name_validator],
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owned_learning_sets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "users",
                    models.ManyToManyField(
                        related_name="used_learning_sets", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FragmentEdit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        default="",
                        validators=[backend.tools.validators.markdown_validator],
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "content",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="backend.content",
                    ),
                ),
                (
                    "fragment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="edit",
                        to="backend.fragment",
                    ),
                ),
                (
                    "learning_sets",
                    models.ManyToManyField(
                        related_name="edits", to="backend.learningset"
                    ),
                ),
            ],
            options={
                "verbose_name": "Document Fragment Edit",
                "verbose_name_plural": "Document Fragment Edits",
            },
        ),
        migrations.AddField(
            model_name="projectassistant",
            name="project",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assistant",
                to="backend.project",
            ),
        ),
        migrations.CreateModel(
            name="Revision",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number", models.IntegerField()),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        validators=[backend.tools.validators.name_validator],
                    ),
                ),
                ("is_latest", models.BooleanField(default=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "predecessor",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="successors",
                        to="backend.revision",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revisions",
                        to="backend.project",
                    ),
                ),
            ],
            options={
                "verbose_name": "Revision",
                "verbose_name_plural": "Revisions",
            },
        ),
        migrations.AddField(
            model_name="projectassistant",
            name="revision",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="backend.revision",
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="revision",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documents",
                to="backend.revision",
            ),
        ),
        migrations.CreateModel(
            name="Transformation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transformer_name",
                    models.CharField(
                        max_length=32,
                        validators=[backend.tools.validators.identifier_validator],
                    ),
                ),
                (
                    "profile_name",
                    models.CharField(
                        max_length=200,
                        validators=[backend.tools.validators.name_validator],
                    ),
                ),
                ("version", models.IntegerField()),
                ("configuration", models.JSONField()),
                ("statistics", models.JSONField(default=dict)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "revision",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transformations",
                        to="backend.revision",
                    ),
                ),
            ],
            options={
                "verbose_name": "Transformation",
                "verbose_name_plural": "Transformations",
            },
        ),
        migrations.CreateModel(
            name="FragmentTransformation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[(0, "Failure"), (1, "Success")], default=0
                    ),
                ),
                ("output", models.TextField(blank=True)),
                ("failure_input", models.TextField(blank=True)),
                ("failure_reason", models.TextField(blank=True)),
                (
                    "content",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="backend.content",
                    ),
                ),
                (
                    "fragment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transformation",
                        to="backend.fragment",
                    ),
                ),
                (
                    "transformation",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="backend.transformation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Document Fragment Transformation",
                "verbose_name_plural": "Document Fragment Transformation",
            },
        ),
        migrations.CreateModel(
            name="TransformerProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "profile_name",
                    models.CharField(
                        max_length=200,
                        validators=[backend.tools.validators.name_validator],
                        verbose_name="Name",
                    ),
                ),
                (
                    "transformer_name",
                    models.CharField(
                        max_length=32,
                        validators=[backend.tools.validators.identifier_validator],
                        verbose_name="Transformer",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        validators=[backend.tools.validators.markdown_validator],
                        verbose_name="Notes",
                    ),
                ),
                ("version", models.IntegerField()),
                ("configuration", models.JSONField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transformer_profiles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Transformer Profile",
                "verbose_name_plural": "Transformer Profiles",
            },
        ),
        migrations.AddField(
            model_name="transformation",
            name="profile",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="backend.transformerprofile",
            ),
        ),
        migrations.CreateModel(
            name="UserSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="settings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User Settings",
            },
        ),
        migrations.CreateModel(
            name="TransformerUserSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transformer_name",
                    models.CharField(
                        max_length=32,
                        validators=[backend.tools.validators.identifier_validator],
                    ),
                ),
                ("version", models.IntegerField()),
                ("configuration", models.JSONField()),
                (
                    "settings",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transformer_settings",
                        to="backend.usersettings",
                    ),
                ),
            ],
            options={
                "verbose_name": "TransformerProfile Settings",
            },
        ),
        migrations.CreateModel(
            name="EgressAssistantDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("order_index", models.IntegerField()),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="backend.document",
                    ),
                ),
                (
                    "egress_assistant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="backend.egressassistant",
                    ),
                ),
            ],
            options={
                "verbose_name": "Egress Assistant Document",
                "verbose_name_plural": "Egress Assistant Documents",
            },
        ),
        migrations.CreateModel(
            name="IngestDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("local_path", models.CharField(max_length=250)),
                (
                    "name",
                    models.CharField(
                        max_length=250,
                        validators=[backend.tools.validators.filename_validator],
                    ),
                ),
                (
                    "folder",
                    models.CharField(
                        blank=True,
                        max_length=250,
                        validators=[backend.tools.validators.folder_validator],
                    ),
                ),
                (
                    "document_syntax",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=32,
                        validators=[
                            backend.tools.validators.optional_identifier_validator
                        ],
                    ),
                ),
                (
                    "planed_action",
                    models.SmallIntegerField(
                        choices=[(0, "Ignore"), (1, "Add")], default=0
                    ),
                ),
                (
                    "ingest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="backend.ingestassistant",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ingest Document",
                "verbose_name_plural": "Ingest Documents",
            },
        ),
        migrations.CreateModel(
            name="TransformationAssistantDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("order_index", models.IntegerField()),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="backend.document",
                    ),
                ),
                (
                    "transformation_assistant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="backend.transformationassistant",
                    ),
                ),
            ],
            options={
                "verbose_name": "Transformation Assistant Document",
                "verbose_name_plural": "Transformation Assistant Documents",
            },
        ),
        migrations.AddField(
            model_name="transformationassistant",
            name="profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="+",
                to="backend.transformerprofile",
            ),
        ),
        migrations.AddField(
            model_name="transformationassistant",
            name="transformation",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="backend.transformation",
            ),
        ),
        migrations.AddIndex(
            model_name="fragment",
            index=models.Index(
                fields=["document", "position"], name="fragment_idx_main"
            ),
        ),
        migrations.AddConstraint(
            model_name="fragment",
            constraint=models.UniqueConstraint(
                fields=("document", "position"), name="fragment_unique_main"
            ),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["modified"], name="project_idx_modified"),
        ),
        migrations.AddIndex(
            model_name="project",
            index=models.Index(fields=["owner"], name="project_idx_owner"),
        ),
        migrations.AddIndex(
            model_name="revision",
            index=models.Index(
                fields=["project", "number"], name="revision_number_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="revision",
            index=models.Index(
                fields=["project", "is_latest"], name="revision_is_latest_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="projectassistant",
            index=models.Index(fields=["project", "user"], name="assist_main_idx"),
        ),
        migrations.AddIndex(
            model_name="projectassistant",
            index=models.Index(fields=["project"], name="ingest_idx_project"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["revision"], name="document_node_idx_main"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["path"], name="document_node_idx_path"),
        ),
        migrations.AddConstraint(
            model_name="document",
            constraint=models.UniqueConstraint(
                fields=("revision", "path"), name="document_node_unique_main"
            ),
        ),
        migrations.AddIndex(
            model_name="transformerprofile",
            index=models.Index(fields=["owner"], name="tf_owner_idx"),
        ),
        migrations.AddIndex(
            model_name="transformerprofile",
            index=models.Index(fields=["profile_name"], name="tf_profile_name_idx"),
        ),
        migrations.AddIndex(
            model_name="transformerprofile",
            index=models.Index(fields=["modified"], name="tf_modified_idx"),
        ),
        migrations.AddIndex(
            model_name="transformation",
            index=models.Index(
                fields=["revision", "created"], name="tra_project_created_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="transformerusersettings",
            index=models.Index(
                fields=["transformer_name"], name="ts_transformer_name_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="transformerusersettings",
            index=models.Index(fields=["settings"], name="ts_settings_idx"),
        ),
        migrations.AddIndex(
            model_name="egressassistantdocument",
            index=models.Index(
                fields=["egress_assistant"], name="eg_assist_doc_main_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="egressassistantdocument",
            index=models.Index(fields=["order_index"], name="eg_assist_doc_order_idx"),
        ),
        migrations.AddIndex(
            model_name="ingestdocument",
            index=models.Index(
                fields=["ingest", "folder", "name"], name="ingest_document_idx_main"
            ),
        ),
        migrations.AddIndex(
            model_name="ingestdocument",
            index=models.Index(fields=["ingest"], name="ingest_document_idx_ingest"),
        ),
        migrations.AddIndex(
            model_name="transformationassistantdocument",
            index=models.Index(
                fields=["transformation_assistant"], name="tr_assist_doc_main_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="transformationassistantdocument",
            index=models.Index(fields=["order_index"], name="tr_assist_doc_order_idx"),
        ),
    ]
