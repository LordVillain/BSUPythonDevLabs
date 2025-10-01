def test_cli_add_student_and_exit(monkeypatch, capsys):
    inputs = iter([
        "4",                    # Добавить студента
        "101",                  # ID
        "Тестов Тест",          # Имя
        "80 90",                # Оценки
        "0"                     # Выход
    ])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    from lab.main import main
    main()

    captured = capsys.readouterr()
    output = captured.out

    assert "Студент добавлен." in output
    assert "Выход." in output