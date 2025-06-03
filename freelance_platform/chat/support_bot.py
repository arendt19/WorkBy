"""
Модуль поддержки с искусственным интеллектом для платформы WorkBy.
Простая реализация без внешних API.
"""
import re
from django.utils.translation import gettext_lazy as _

# Словарь с часто задаваемыми вопросами и ответами
# Структура: {
#   'ключевые_слова': {
#       'ru': 'ответ на русском',
#       'en': 'ответ на английском',
#       'kk': 'ответ на казахском'
#   }
# }
FAQ_RESPONSES = {
    'регистрация|зарегистрироваться|создать аккаунт|signup|register': {
        'ru': 'Для регистрации на платформе WorkBy нажмите кнопку "Регистрация" в правом верхнем углу сайта. Вы можете зарегистрироваться как фрилансер или как клиент. Заполните все необходимые поля и подтвердите адрес электронной почты.',
        'en': 'To register on the WorkBy platform, click the "Sign Up" button in the top right corner of the site. You can register as a freelancer or as a client. Fill in all the required fields and confirm your email address.',
        'kk': 'WorkBy платформасында тіркелу үшін сайттың жоғарғы оң жақ бұрышындағы "Тіркелу" түймесін басыңыз. Сіз фрилансер немесе клиент ретінде тіркеле аласыз. Барлық қажетті өрістерді толтырып, электрондық пошта мекенжайыңызды растаңыз.'
    },
    'оплата|платеж|деньги|перевод|payment|withdraw|вывод': {
        'ru': 'WorkBy использует систему безопасных платежей с эскроу. Клиент вносит оплату, которая блокируется до завершения работы. После принятия работы средства автоматически переводятся фрилансеру. Для вывода средств перейдите в раздел "Кошелек" и выберите удобный способ.',
        'en': 'WorkBy uses a secure payment system with escrow. The client makes a payment, which is held until the work is completed. After accepting the work, funds are automatically transferred to the freelancer. To withdraw funds, go to the "Wallet" section and choose a convenient method.',
        'kk': 'WorkBy эскроу арқылы қауіпсіз төлем жүйесін қолданады. Клиент жұмыс аяқталғанға дейін бұғатталатын төлем жасайды. Жұмысты қабылдағаннан кейін қаражат фрилансерге автоматты түрде аударылады. Қаражатты шығару үшін "Әмиян" бөліміне өтіп, ыңғайлы әдісті таңдаңыз.'
    },
    'проект|задание|заказ|project|task|job': {
        'ru': 'Чтобы создать новый проект, войдите в свой аккаунт клиента, перейдите в раздел "Проекты" и нажмите "Создать проект". Заполните информацию о проекте, включая название, описание, бюджет и сроки. Вы можете добавить файлы и указать необходимые навыки.',
        'en': 'To create a new project, log in to your client account, go to the "Projects" section and click "Create Project". Fill in information about the project, including title, description, budget, and deadlines. You can add files and specify required skills.',
        'kk': 'Жаңа жоба жасау үшін клиент тіркелгіңізге кіріп, "Жобалар" бөліміне өтіп, "Жоба жасау" түймесін басыңыз. Жоба туралы ақпаратты толтырыңыз, оның ішінде атауы, сипаттамасы, бюджеті және мерзімдері. Сіз файлдарды қосып, қажетті дағдыларды көрсете аласыз.'
    },
    'профиль|портфолио|profile|portfolio': {
        'ru': 'Для редактирования профиля перейдите в раздел "Мой профиль". Там вы можете обновить личную информацию, добавить навыки, образование и опыт работы. Фрилансеры могут загружать работы в портфолио для привлечения клиентов.',
        'en': 'To edit your profile, go to the "My Profile" section. There you can update personal information, add skills, education, and work experience. Freelancers can upload works to their portfolio to attract clients.',
        'kk': 'Профильді өңдеу үшін "Менің профилім" бөліміне өтіңіз. Онда сіз жеке ақпаратты жаңартып, дағдыларды, білімді және жұмыс тәжірибесін қоса аласыз. Фрилансерлер клиенттерді тарту үшін портфолиоға жұмыстарын жүктей алады.'
    },
    'контракт|сделка|contract|deal': {
        'ru': 'Контракт заключается после того, как клиент принимает предложение фрилансера. В контракте указываются условия работы, сроки, этапы и сумма оплаты. После завершения работы и подтверждения клиентом, платеж переводится фрилансеру.',
        'en': 'A contract is concluded after the client accepts the freelancer\'s proposal. The contract specifies the terms of work, deadlines, milestones, and payment amount. After completion of the work and confirmation by the client, the payment is transferred to the freelancer.',
        'kk': 'Келісімшарт клиент фрилансердің ұсынысын қабылдағаннан кейін жасалады. Келісімшартта жұмыс шарттары, мерзімдері, кезеңдері және төлем сомасы көрсетіледі. Жұмыс аяқталып, клиент растағаннан кейін төлем фрилансерге аударылады.'
    },
    'отзыв|рейтинг|review|rating|feedback': {
        'ru': 'После завершения проекта и клиент, и фрилансер могут оставить отзывы друг о друге. Рейтинг формируется на основе отзывов и влияет на видимость профиля в поиске. Высокий рейтинг помогает получать больше заказов и устанавливать более высокие ставки.',
        'en': 'After completing the project, both the client and the freelancer can leave reviews about each other. The rating is formed based on reviews and affects the visibility of the profile in search. A high rating helps to get more orders and set higher rates.',
        'kk': 'Жобаны аяқтағаннан кейін клиент те, фрилансер де бір-бірі туралы пікір қалдыра алады. Рейтинг пікірлер негізінде қалыптасады және профильдің іздеудегі көрінуіне әсер етеді. Жоғары рейтинг көбірек тапсырыс алуға және жоғары бағаларды белгілеуге көмектеседі.'
    },
    'техподдержка|помощь|поддержка|support|help': {
        'ru': 'Если у вас возникли вопросы или проблемы, вы можете обратиться в службу поддержки через форму обратной связи на сайте или написать на email support@workby.com. Наша команда постарается ответить вам в течение 24 часов.',
        'en': 'If you have questions or problems, you can contact support through the feedback form on the site or write to support@workby.com. Our team will try to respond within 24 hours.',
        'kk': 'Сұрақтарыңыз немесе мәселелеріңіз болса, сайттағы кері байланыс формасы арқылы немесе support@workby.com электрондық поштасына жазу арқылы қолдау қызметіне хабарласа аласыз. Біздің команда 24 сағат ішінде жауап беруге тырысады.'
    },
    'комиссия|сервисный сбор|commission|fee': {
        'ru': 'WorkBy взимает комиссию в размере 10% от суммы проекта. Комиссия автоматически вычитается из суммы, которую получает фрилансер. Клиенты не платят дополнительную комиссию сверх указанной стоимости проекта.',
        'en': 'WorkBy charges a commission of 10% of the project amount. The commission is automatically deducted from the amount received by the freelancer. Clients do not pay additional commission beyond the specified project cost.',
        'kk': 'WorkBy жоба сомасының 10% мөлшерінде комиссия алады. Комиссия фрилансер алатын сомадан автоматты түрде шегеріледі. Клиенттер көрсетілген жоба құнынан тыс қосымша комиссия төлемейді.'
    },
    'спор|конфликт|dispute|conflict': {
        'ru': 'В случае возникновения споров между клиентом и фрилансером, вы можете открыть спор в разделе контракта. Администрация WorkBy рассмотрит ситуацию и поможет найти справедливое решение для обеих сторон.',
        'en': 'In case of disputes between the client and freelancer, you can open a dispute in the contract section. The WorkBy administration will review the situation and help find a fair solution for both parties.',
        'kk': 'Клиент пен фрилансер арасында дау туындаған жағдайда, келісімшарт бөлімінде дау аша аласыз. WorkBy әкімшілігі жағдайды қарастырып, екі тарап үшін де әділ шешім табуға көмектеседі.'
    }
}

def get_support_response(query, language='ru'):
    """
    Получить ответ от бота поддержки на основе запроса пользователя
    
    Args:
        query (str): Текст запроса пользователя
        language (str): Код языка (ru, en, kk)
        
    Returns:
        str: Ответ бота поддержки
    """
    # Нормализация запроса
    query = query.lower().strip()
    
    # Проверка на приветствие
    if re.search(r'привет|здравствуйте|добрый день|hello|hi|сәлем', query):
        greetings = {
            'ru': 'Здравствуйте! Я виртуальный помощник платформы WorkBy. Чем могу помочь вам сегодня?',
            'en': 'Hello! I am the virtual assistant of the WorkBy platform. How can I help you today?',
            'kk': 'Сәлеметсіз бе! Мен WorkBy платформасының виртуалды көмекшісімін. Бүгін сізге қалай көмектесе аламын?'
        }
        return greetings.get(language, greetings['ru'])
    
    # Поиск по ключевым словам
    for keywords, responses in FAQ_RESPONSES.items():
        if re.search(keywords, query):
            return responses.get(language, responses['ru'])
    
    # Ответ по умолчанию, если не найдено совпадений
    default_responses = {
        'ru': 'Извините, я не могу найти информацию по вашему запросу. Попробуйте сформулировать вопрос иначе или обратитесь в службу поддержки по адресу support@workby.com.',
        'en': 'Sorry, I cannot find information on your request. Try rephrasing your question or contact support at support@workby.com.',
        'kk': 'Кешіріңіз, сұрауыңыз бойынша ақпарат таба алмадым. Сұрағыңызды басқаша тұжырымдап көріңіз немесе support@workby.com мекенжайы бойынша қолдау қызметіне хабарласыңыз.'
    }
    return default_responses.get(language, default_responses['ru'])
