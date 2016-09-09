#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime, date, timedelta

import click

import trackmac.app
import trackmac.config
import trackmac.utils


class MutuallyExclusiveOption(click.Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise click.UsageError(
                '`--{name}` is mutually exclusive with the following options: '
                '{options}'.format(name=self.name.replace('_', ''),
                                   options=', '
                                   .join(['`--{}`'.format(_) for _ in
                                          self.mutually_exclusive]))
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx, opts, args
        )


_SHORTCUT_OPTIONS = ['month', 'week', 'day']


@click.group()
@click.version_option(version=trackmac.config.VERSION, prog_name='Trackmac')
@click.pass_context
def cli(ctx):
    ctx.obj = trackmac.app.TimeTracking()


@cli.command()
@click.pass_context
def setup(ctx):
    """
    setup the track all necessary files.
    """
    trackmac.utils.create_dir()
    trackmac.utils.create_database()
    trackmac.utils.symlink_and_load_plist()
    click.echo('Done.')


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@cli.command()
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to delete trackmac data folder?')
@click.pass_context
def drop(ctx):
    """
    delete the track all necessary files.
    """
    trackmac.utils.load_or_unload_daemon('unload')
    trackmac.utils.remove_all_files()
    click.echo('Done.')


@cli.command()
@click.pass_context
def stop(ctx):
    """
    Unload the track daemon mannualy.
    """
    click.echo(trackmac.utils.load_or_unload_daemon('unload'))


@cli.command()
@click.pass_context
def start(ctx):
    """
    Load the track daemon mannualy.
    """
    if not trackmac.utils.has_set_up():
        click.echo(trackmac.utils.style('error', 'Could not find db or plist file.Run `tm setup` first.\n'))
        ctx.abort()
    click.echo(trackmac.utils.load_or_unload_daemon('load'))


@cli.command()
@click.pass_obj
@click.argument('web', required=False)
@click.pass_context
@click.option('-f', '--from', 'start_', cls=MutuallyExclusiveOption, type=str,
              default=date.today().strftime("%Y-%m-%d"),
              mutually_exclusive=_SHORTCUT_OPTIONS,
              help="The date from when the report should start.Format:%Y-%m-%d")
@click.option('-t', '--to', 'end_', cls=MutuallyExclusiveOption, type=str,
              default=date.today().strftime("%Y-%m-%d"),
              mutually_exclusive=_SHORTCUT_OPTIONS,
              help="The date at which the report should stop (inclusive).Format:%Y-%m-%d")
@click.option('-w', '--week', cls=MutuallyExclusiveOption, type=str,
              flag_value=trackmac.utils.get_start_date_for_period('week'),
              mutually_exclusive=['day', 'month', 'year'],
              help='Reports application usage for current week.')
@click.option('-m', '--month', cls=MutuallyExclusiveOption, type=str,
              flag_value=trackmac.utils.get_start_date_for_period('month'),
              mutually_exclusive=['week', 'day', 'year'],
              help='Reports application usage for current month')
@click.option('-d', '--day', cls=MutuallyExclusiveOption, type=str,
              flag_value=trackmac.utils.get_start_date_for_period('day'),
              mutually_exclusive=['week', 'month', 'year'],
              help='Reports application usage for yesterday.')
@click.option('-n', '--num', type=int, default=10,
              help='Only show top n applications(default to 10).')
@click.option('-T', '--tags', 'tags', is_flag=True,
              help="Reports application usage group by tags")
@click.option('-O', '--output',
              type=click.Path(file_okay=True, dir_okay=True, writable=True, resolve_path=True),
              help="Output json data to the specified file")
def list(ctx, tt, web, start_, end_, week, month, day, num, tags, output):
    """
    Display applications being tracked.

    Add web to show web sites being tracked.

    Example:

    \b
    $ tm list

        2016 Sep 05 - 2016 Sep 06\n
        ─────────────────────────────\n
        Google Chrome     32m 09s  ████████████████████ 66.6%\n
        终端               08m 28s  █████ 17.5%


    $ tm list web

        2016 Sep 05 - 2016 Sep 06\n
        ─────────────────────────────\n
        https://github.com/       06m 12s  ██████ 19.2%\n
        https://www.v2ex.com/     06m 01s  ██████ 18.6%

    $ tm list web -w -n 100 -O trackdata.json

    Successfully written to /position/to/trackdata.json

    """
    if not trackmac.utils.has_set_up():
        click.echo(trackmac.utils.style('error', 'Could not find db or plist file.Run `tm setup` first.\n'))
        ctx.abort()

    if tt.is_not_running:
        click.echo(trackmac.utils.style('error', 'Warning:Trackmac daemon not running.Run `tm start` first.\n'))

    start_ = datetime.strptime(start_, "%Y-%m-%d").date()
    for start_date in (_ for _ in [day, week, month]
                       if _ is not None):
        start_ = start_date
    end = datetime.strptime(end_, "%Y-%m-%d").date() + timedelta(days=1)
    if start_ > end:
        raise click.ClickException("'from' must be anterior to 'to'")
    if tags:
        records = tt.report(start_, end, 'tag_name')
        name = 'tag_name'
        others = sum(records.pop(i)['duration'] for (i, r) in enumerate(records) if not r[name])
        if others:
            records.append({'tag_name': 'Others', 'duration': others})
    elif web and web.lower() == 'web':
        records = tt.web_report(start_, end)
        name = 'domain'
    elif web is None:
        records = tt.report(start_, end, 'app_name')
        name = 'app_name'
    else:
        raise click.UsageError(
            'Use `web` to display web browsing statistics',
        )
    if not records:
        click.echo(trackmac.utils.style('time', 'No data being collected.Please wait for a moment.'))
        return
    records = sorted(records, key=lambda x: x['duration'], reverse=True)[:num]
    max_len = max(len(rec[name].encode("utf8")) for rec in records if rec[name])
    # output to file
    if output:
        try:
            with open(output, 'w') as f:
                json.dump(records, f)
        except IOError:
            raise click.FileError(output, hint='IOError')
        else:
            click.echo(trackmac.utils.style('time', 'Successfully written to {}'.format(output)))
    else:
        click.echo(trackmac.utils.style('date', "\t" + trackmac.utils.fill_text_to_print_width(
            start_.strftime("%Y %b %d") + " - " + end.strftime("%Y %b %d"), max_len + 22)))
        click.echo(trackmac.utils.style('date', "\t" + trackmac.utils.fill_text_to_print_width(u"─" * 29, max_len + 24)))
        total_time = sum(r['duration'] for r in records)
        for rec in records:
            click.echo(u"\t{project} {time} {percentage}".format(
                time=trackmac.utils.style('time', '{:>11}'.format(trackmac.utils.format_timedelta(rec['duration']))),
                project=trackmac.utils.style(
                    'project', trackmac.utils.fill_text_to_print_width((rec[name] or 'Others'), max_len)
                ),
                percentage=trackmac.utils.style('tag', trackmac.utils.get_progress(rec['duration'], total_time))
            ))


@cli.command()
@click.argument('app_name', required=False)
@click.pass_obj
@click.pass_context
@click.option('-d', '--delete', type=str,
              help='Remove blocked application')
def block(ctx, tt, app_name, delete):
    """
    Stop tracking specified application.

    If app name contains spaces,use `\` before them.

    Example:

    \b
    $ tm block Google\ Chrome
    Applocation Google Chrome blocked.

    $ tm block -d Google\ Chrome
    Applocation Google Chrome unblocked.
    """
    name = delete or app_name
    if name:
        if tt.block(name, delete is None):
            click.echo(trackmac.utils.style('time', u'Successfully {}blocked {}.'.format('un'if delete else'', name)))
        else:
            click.echo(trackmac.utils.style('error', u'Appication {} not found.'.format(name)))
    else:
        click.echo(u"\tBlocked applications:\n \t\t[{apps}]".format(apps=trackmac.utils.style('project', ",".join(tt.black_list))))


@cli.command()
@click.option('-a', '--add', 'param', nargs=2, type=click.STRING,
              help='the tag to add', required=False)
@click.pass_obj
@click.pass_context
def tag(ctx, tt, param):
    """
    Add a new tag for grouping applications.

    example:

    $ tm tag -a Developing Pycharm

    """
    if not param:
        for t in tt.tags:
            click.echo(u"\t{tag}\n \t\t[{apps}]".format(tag=trackmac.utils.style('tag', t['tag_name']),
                                                        apps=trackmac.utils.style('project', t['app_names'])))
    elif tt.add_tag(*param):
        click.echo(trackmac.utils.style('time', 'Successfully added tag.'))
    else:
        click.echo(trackmac.utils.style('error', 'Application name not found.'))


@cli.command()
@click.argument('command', required=False)
@click.pass_context
def help(ctx, command):
    """
    Display help information
    """
    if not command:
        click.echo(ctx.parent.get_help())
        return

    cmd = cli.get_command(ctx, command)

    if not cmd:
        raise click.ClickException("No such command: {}".format(command))

    click.echo(cmd.get_help(ctx))


if __name__ == '__main__':
    cli()
