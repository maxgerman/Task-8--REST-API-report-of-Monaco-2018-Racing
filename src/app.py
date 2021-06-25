from flask import Flask, render_template, request, redirect, url_for, session
import wikipedia
import re
from src.drivers import Driver

app = Flask(__name__)
app.secret_key = 'dev'


def wiki(driver_name: str) -> str:
    """Return the info about driver from wikipedia"""
    content = wikipedia.page(driver_name).content
    with_headings = re.sub(r'=+\s*(.*?)\s*=+', r'<b>\1</b>', content)
    return with_headings


@app.route('/report', methods=['GET', 'POST'])
def common_report() -> "Response":
    """
    Show the report for all drivers.
    Sort and set the order switch based on url for the template. 
    """
    if request.args.get('order') == 'desc':
        asc_order = False
    else:
        asc_order = True
    session['report_desc_switch'] = not asc_order

    if request.method == 'POST':
        if request.form.get('desc_switch'):
            session['report_desc_switch'] = True
            return redirect(url_for('common_report', order='desc'))
        else:
            session['report_desc_switch'] = False
            return redirect(url_for('common_report'))

    lines = Driver.print_report(asc=asc_order).split('\n')
    return render_template('report.html', lines=lines)


@app.route('/drivers', methods=['GET', 'POST'])
def list_drivers() -> "Response":
    """Show ordered driver list as 'name - abbreviation' """
    if request.method == 'POST':
        if request.form.get('desc_switch'):
            session['driver_desc_switch'] = True
            return redirect(url_for('list_drivers', order='desc'))
        else:
            session['driver_desc_switch'] = False
            return redirect(url_for('list_drivers'))

    driver_id = request.args.get('driver_id')
    driver_info = ''
    if driver_id:
        drivers = Driver.get_by_id(driver_id)
        try:
            driver_info = wiki(drivers[0].name)
        except (TypeError, IndexError, wikipedia.PageError):
            driver_info = None
    else:
        asc_order = False if request.args.get('order') == 'desc' else True
        session['driver_desc_switch'] = not asc_order
        drivers = Driver.all(asc=asc_order)
    return render_template('drivers.html', drivers=drivers, driver_info=driver_info)


@app.route('/')
def home() -> "Response":
    return redirect(url_for('common_report'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('base.html', error=404)

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', context=500)


if __name__ == '__main__':
    Driver.build_report()
    app.run()
