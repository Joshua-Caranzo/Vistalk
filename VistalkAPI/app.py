from flask import Flask, request, jsonify
from flask_cors import CORS
import user, section, content, question, shop, emailService, feedback, report, dailytask,dashboard, recording
import db
from functools import wraps
import jwt

app = Flask(__name__)
CORS(app)

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] 
        
        if not token:
            return jsonify({'message': 'Unauthorized!'}), 401
        
        try:
            data = jwt.decode(token, db.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    
    return decorator

@app.route('/login', methods=['GET'])
def login_admin():
    return user.login()

@app.route('/saveSection', methods=['POST'])
@token_required
def saveSection():
    return section.save_section()

@app.route('/getSections', methods=['GET'])
@token_required
def getSections():
    return section.get_Sections()

@app.route('/getLanguages', methods=['GET'])
def getLanguages():
    return section.get_Language()

@app.route('/saveUnit', methods=['POST'])
@token_required
def saveUnit():
    return section.save_units()

@app.route('/getUnits', methods=['GET'])
@token_required
def getUnits():
    return section.get_Units()

@app.route('/getContentTypes', methods=['GET'])
@token_required
def getContentTypes():
    return content.get_ContentTypes()

@app.route('/saveContent', methods=['POST'])
@token_required
def saveContent():
    return content.save_content()

@app.route('/getContents', methods=['GET'])
def getcontent():
    return content.get_Contents()

@app.route('/getContentsAll', methods=['GET'])
def get_Contents_All():
    return content.get_Contents_All()

@app.route('/getContentById', methods=['GET'])
@token_required
def getcontentById():
    return content.getContentById()

@app.route('/getSyllablesByContentId', methods=['GET'])
@token_required
def getSyllablesByContentId():
    return content.getSyllablesByContentId()

@app.route('/getDefinitionByContentId', methods=['GET'])
@token_required
def getDefinitionByContentId():
    return content.getDefinitionByContentId()

@app.route('/getExamplesByContentId', methods=['GET'])
@token_required
def getExamplesByContentId():
    return content.getExamplesByContentId()

@app.route('/getFileByFileName', methods=['GET'])
def getFileByFileName():
    return content.getFileByFileName()

@app.route('/getQuestionTypes', methods=['GET'])
@token_required
def get_QuestionTypes():
    return question.get_QuestionTypes()

@app.route('/getChoices', methods=['GET'])
@token_required
def get_choices():
    return question.get_choices()

@app.route('/saveQuestionMultiple', methods=['POST'])
@token_required
def save_questionMultiple():
    return question.save_questionMultiple()

@app.route('/savequestionMatch', methods=['POST'])
@token_required
def save_questionMatch():
    return question.save_question_match()
  
@app.route('/getItemType', methods=['GET'])
@token_required
def getItemTypes():
    return shop.getItemType()

@app.route('/saveItemShop', methods=['POST'])
@token_required
def saveItem():
    return shop.save_item()
  
@app.route('/contentInactive', methods=['PUT'])
@token_required
def contentInactive():
    return content.contentInactive()

@app.route('/sectionInactive', methods=['PUT'])
@token_required
def sectionInactive():
    return section.sectionInactive()

@app.route('/unitInactive', methods=['PUT'])
@token_required
def unitInactive():
    return section.unitInactive()

@app.route('/questionInactive', methods=['PUT'])
@token_required
def questionInactive():
    return question.questionInactive()

@app.route('/registerUser', methods=['POST'])
def registerVista():
    return user.createVista()

@app.route('/loginVista', methods=['GET'])
def loginVista():
    return user.loginVista()

@app.route('/getQuestions', methods=['GET'])
@token_required
def getQuestions():
    return question.get_Questions()

@app.route('/getMultipleChoice', methods=['GET'])
@token_required
def getMultipleChoice():
    return question.get_multiple_choice()

@app.route('/getMatchingType', methods=['GET'])
@token_required
def getMatchingType():
    return question.get_matching_type()  

@app.route('/forgotPassword', methods=['GET'])
def forgotPassword():
    return emailService.send_code_to_email()  

@app.route('/verifyCode', methods=['GET'])
def verifyCode():
    return emailService.verify_code()  

@app.route('/changePassword', methods=['PUT'])
def changePassword():
    return user.forgotPassword()  

@app.route('/getItemList', methods=['GET'])
@token_required
def getItemList():
    return shop.get_items()  

@app.route('/getShopFileByFileName', methods=['GET'])
def getShopFileByFileName():
    return shop.getShopFileByFileName()  

@app.route('/itemInactive', methods=['PUT'])
@token_required
def setItemInactive():
    return shop.itemInactive()  

@app.route('/coinBagInactive', methods=['PUT'])
@token_required
def coinBagInactive():
    return shop.coinBagInactive()

@app.route('/getQuestionFiles', methods=['GET'])
def getQuestionFile():
    return question.getQuestionFile()  

@app.route('/getusers', methods=['GET'])
@token_required
def get_Users():
    return user.get_Users()  

@app.route('/getuserPowerUps', methods=['GET'])
@token_required
def get_UserPowerUps():
    return user.get_UserPowerUps()  

@app.route('/isEmailUse', methods=['GET'])
def is_email_used():
    return emailService.is_email_used()  

@app.route('/editVistaProfile', methods=['PUT'])
def editVistaProfile():
    return user.editVistaProfile()
  
@app.route('/deactivateVistaAccount', methods=['PUT'])
def deactivateVistaAccount():
    return user.deactivateVistaAccount()  

@app.route('/getFeedbacks', methods=['GET'])
@token_required
def getFeedbacks():
    return feedback.get_feedback()  

@app.route('/getReports', methods=['GET'])
@token_required
def getReports():
    return report.get_report()

@app.route('/reportResponded', methods=['PUT'])
@token_required
def reportResponded():
    return report.reportResponded()

@app.route('/getDailyTask', methods=['GET'])
@token_required
def getDailyTask():
    return dailytask.get_dailytask()

@app.route('/getDailyTaskTypes', methods=['GET'])
@token_required
def getDailyTaskTypes():
    return dailytask.get_DailyTaskType()

@app.route('/saveDailyTask', methods=['POST'])
@token_required
def saveDailyTask():
    return dailytask.save_dailyTask()

@app.route('/getUserDetails', methods=['GET'])
@token_required
def getUserDetails():
    return user.getUserDetails()

@app.route('/getUserImage', methods=['GET'])
def getUserImage():
    return user.getUserImage()

@app.route('/reActivateVista', methods=['PUT'])
def reActivateVista():
    return user.reActivateVista()

@app.route('/getLeaderBoard', methods=['GET'])
def getLeaderBoard():
    return dashboard.getLeaderBoards()

@app.route('/getStatusVista', methods=['GET'])
def getStatusVista():
    return dashboard.getStatusVista()

@app.route('/getLanguageUsers', methods=['GET'])
def getLanguageUsers():
    return dashboard.getLanguageUsers()

@app.route('/getSubscriptionData', methods=['GET'])
def getSubscriptionData():
    return dashboard.getSubscriptionData()

@app.route('/deleteDailyTask', methods=['PUT'])
def deleteDailyTask():
    return dailytask.deleteDailyTask()

@app.route('/sendEmailToUs', methods=['POST'])
def sendEmailToUs():
    return emailService.sendEmailToUs()

@app.route('/salesReport', methods=['GET'])
def salesReport():
    return dashboard.salesReport()

@app.route('/salesReportCoinBags', methods=['GET'])
def salesReportCoinBags():
    return dashboard.salesReportCoinBags()

@app.route('/salesSubscriptions', methods=['GET'])
def salesSubscriptions():
    return dashboard.salesSubscriptions()

@app.route('/getTotalSales', methods=['GET'])
def getTotalSales():
    return dashboard.getTotalSales()

@app.route('/getPowerUps', methods=['GET'])
def getPowerUps():
    return dailytask.get_powerUps()


@app.route('/getUserRatings', methods=['GET'])
def userRatings():
    return dashboard.userRatings()

@app.route('/saveAudio', methods=['POST'])
def saveAudioContent():
    return recording.save_content()

@app.route('/getRecordingContents', methods=['GET'])
def getRecordingContents():
    return recording.get_contents()

@app.route('/getRecordingByFileName', methods=['GET'])
def getRecordingByFileName():
    return recording.getRecordingByFileName()

@app.route('/acceptRecording', methods=['PUT'])
def acceptRecording():
    return recording.acceptRecording()

@app.route('/rejectRecording', methods=['PUT'])
def rejectRecording():
    return recording.rejectRecording()

@app.route('/getPronunciationProgress', methods=['GET'])
def getPronunciationProgress():
    return dashboard.getPronunciationProgress()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


