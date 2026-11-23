from tomcam.config import theme


def draw_header(app, title, subtitle=None):
    app.render_text("TOMCAM", 42, 22, theme.ACCENT, 18)
    app.render_text(title, 42, 51, theme.TEXT, 40)
    if subtitle:
        app.render_text(subtitle, 44, 101, theme.MUTED, 18)


