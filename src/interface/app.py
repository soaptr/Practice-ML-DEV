import streamlit as st
import requests


API_URL = "http://localhost:8000"


# Функции для взаимодействия с FastAPI сервером
def login(username, password):
    response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
    return response.json() if response.status_code == 200 else None


def register(username, password):
    response = requests.post(f"{API_URL}/register", json={"name": username, "password": password})
    return response.json() if response.status_code == 200 else None


def get_predictions(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/predictions", headers=headers)
    return response.json() if response.status_code == 200 else []


def send_prediction_data(model_id, data, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/predict", json={"predictor_id": model_id, **data}, headers=headers)
    return response.json() if response.status_code == 200 else None


def get_predictors(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/predictors", headers=headers)
    return response.json() if response.status_code == 200 else []


def get_user_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/user", headers=headers)
    return response.json() if response.status_code == 200 else None


# Интерфейс Streamlit
st.title("Предсказание возраста человека по анализам")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# Форма для авторизации
if choice == "Login":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')
    if st.sidebar.button("Login"):
        login_data = login(username, password)
        if login_data:
            user_data = get_user_data(login_data["access_token"])
            if user_data:
                st.sidebar.success(f"Logged in as {user_data['name']}")
                st.sidebar.text(f"Баланс: {user_data['balance']}")
                st.session_state['token'] = login_data["access_token"]
                st.session_state['user_name'] = user_data['name']
                st.session_state['balance'] = user_data['balance']
        else:
            st.sidebar.error(f"Wrong login or password")

# Форма для регистрации
elif choice == "Register":
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type='password')
    if st.sidebar.button("Register"):
        result = register(new_username, new_password)
        if result:
            st.sidebar.success("Аккаунт успешно создан")
            st.sidebar.info("Перейдите в меню входа, чтобы войти")

# Функционал после аутентификации
if 'token' in st.session_state:
    st.subheader(f"Добро пожаловать, {st.session_state['user_name']}")
    predictors = get_predictors(st.session_state['token'])
    if not predictors:
        st.error("Не удалось получить список моделей")
    else:
        # Формирование списка с названиями и стоимостью моделей
        predictor_options = [f"{pred['name']} (Стоимость: {pred['cost']})" for pred in predictors]
        predictor_mapping = {option: predictors[i]['id'] for i, option in enumerate(predictor_options)}

        st.subheader("Сделать новое предсказание")
        selected_option = st.selectbox("Выберите модель", predictor_options)
        selected_model_id = predictor_mapping[selected_option]

        data_input = {
            "RIAGENDR": st.number_input("RIAGENDR"),
            "PAQ605": st.number_input("PAQ605"),
            "BMXBMI": st.number_input("BMXBMI"),
            "LBXGLU": st.number_input("LBXGLU"),
            "DIQ010": st.number_input("DIQ010"),
            "LBXGLT": st.number_input("LBXGLT"),
            "LBXIN": st.number_input("LBXIN")
        }

        if st.button("Предсказать"):
            prediction = send_prediction_data(selected_model_id, data_input, st.session_state['token'])

            # Обновление баланса пользователя после предсказания
            updated_user_data = get_user_data(st.session_state['token'])
            if updated_user_data:
                st.session_state['balance'] = updated_user_data['balance']
                st.sidebar.text(f"Баланс: {st.session_state['balance']}")

    # Просмотр списка предсказаний
    st.subheader("Мои предсказания")
    if st.button("Показать предсказания"):
        st.sidebar.text(f"Баланс: {st.session_state['balance']}")
        predictions = get_predictions(st.session_state['token'])
        predictions_data = []
        for pred in predictions:
            if pred['result'] == 0:
                result = "Adult"
            elif pred['result'] == 1:
                result = "Senior"
            else:
                result = None

            predictions_data.append({
                "Модель": pred['predictor_name'],
                "Входные данные": f"[{pred['RIAGENDR']}, {pred['PAQ605']}, {pred['BMXBMI']}, {pred['LBXGLU']}, "
                                  f"{pred['DIQ010']}, {pred['LBXGLT']}, {pred['LBXIN']}]",
                "Статус": pred['status'],
                "Результат": result
            })

        if predictions_data:
            st.table(predictions_data)
        else:
            st.write("Нет доступных предсказаний.")
