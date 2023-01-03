from .models import *
from rest_framework import serializers, status
from rest_framework.response import Response as Res


class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = '__all__'

class QuestionnaireParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire_Participants
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class QuestionResponseSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    class Meta:
        model = Answer
        fields = '__all__'


class StartQuestionnaireSerializer (serializers.ModelSerializer):
    class Meta:
        model = Started_Questionnaire
        fields = ('id')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = '__all__'

    def validate(self, value):
        question = value['question']
        answer = value['answer']
        session = value['session']
        if End_Questionnaire.objects.filter(session=session).count() > 0:
            raise serializers.ValidationError({
                "success": False,
                "error": "Session already Ended"
            })

        if answer.question_id != question.id:
            serializer = QuestionSerializer(question)
            queryset = Answer.objects.filter(question=question)
            ans_ser = AnswerSerializer(queryset, many=True)
            raise serializers.ValidationError({
                "success": False,
                "error": "Response Provided not associated with Question",
                "Question": serializer.data,
                "Ans": ans_ser.data,
                "session_id": value['session'].id
            })
        else:
            return value


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class AnswerAllSerializer(serializers.ModelSerializer):
    Answer_ID = serializers.IntegerField(source='id')
    AnswerName = serializers.CharField(source='option')
    class Meta:
        model = Answer
        fields = ('Answer_ID', 'AnswerName')

class DependancySerializer(serializers.ModelSerializer):
    Dependancy_ID = serializers.IntegerField(source='id')
    Answer_ID = serializers.IntegerField(source='answer_id')
    Question_ID = serializers.CharField(source='question_id')
    class Meta:
        model = QuestionDependance
        fields = ('Dependancy_ID','Answer_ID', 'Question_ID')


class QuestionSetSerializer(serializers.ModelSerializer):
    Question_ID = serializers.IntegerField(source='id')
    QuestionName = serializers.CharField(source='question')
    QuestionOrder= serializers.CharField(source='question_order')
    QuestionType= serializers.CharField(source='question_type')
    
    class Meta:
        model = Question
        fields = ('Question_ID', 'QuestionName', 'QuestionOrder','QuestionType')




class DependancySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionDependance
        fields = '__all__'


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class QuestionsSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    dependancy_details = serializers.SerializerMethodField()
    def get_answers(self, obj):
        return AnswersSerializer(obj.answer_set.all(), many=True).data
    
    def get_dependancy_details(self, obj):
        return DependancySerializer(obj.questiondependance_set.all(), many=True).data
    
    class Meta:
        model = Question
        fields = '__all__'


class QuestionAnswDepSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField() 
    # Questions = serializers.SerializerMethodField()
    
    def get_questions(self, instance):
        return QuestionsSerializer(instance.question_set.all().order_by('question_order'), many=True).data

    class Meta:
        model = Questionnaire
        fields = ('__all__')
        