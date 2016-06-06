#ifndef MAINWINDOWBIS_H
#define MAINWINDOWBIS_H

#include <QMainWindow>

namespace Ui {
class MainWindowBIS;
}

class MainWindowBIS : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindowBIS(QWidget *parent = 0);
    ~MainWindowBIS();

private:
    Ui::MainWindowBIS *ui;
};

#endif // MAINWINDOWBIS_H
