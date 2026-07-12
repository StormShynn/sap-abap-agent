import * as vscode from 'vscode';

function quoteForShell(value: string): string {
    return /\s/.test(value) ? `"${value}"` : value;
}

export function activate(context: vscode.ExtensionContext) {
    const disposables: vscode.Disposable[] = [];

    // Register MCP server definition provider
    const provider = vscode.lm.registerMcpServerDefinitionProvider('sap-btp-mcp', {
        provideMcpServerDefinitions: async (_token: vscode.CancellationToken) => {
            const config = vscode.workspace.getConfiguration('sapBtpMcp');
            const command = config.get<string>('command', 'sap-btp-agent');
            const args = config.get<string[]>('args', []);
            const profile = config.get<string>('profile', '');

            const env: Record<string, string | number | null> = {};
            if (profile) {
                env['SAP_BTP_PROFILE'] = profile;
            }

            const def: vscode.McpStdioServerDefinition = {
                command,
                label: 'SAP BTP Agent',
                args,
                env,
            };

            return [def];
        }
    });
    disposables.push(provider);

    // Command: check connection
    disposables.push(
        vscode.commands.registerCommand('sapBtpMcp.checkConnection', async () => {
            const config = vscode.workspace.getConfiguration('sapBtpMcp');
            const command = config.get<string>('command', 'sap-btp-agent');
            const profile = config.get<string>('profile', '');
            const terminal = vscode.window.createTerminal('SAP BTP');
            terminal.show();
            const profileArg = profile ? ` ${quoteForShell(profile)}` : '';
            terminal.sendText(`${quoteForShell(command)} connect${profileArg}`);
        })
    );

    // Command: open settings
    disposables.push(
        vscode.commands.registerCommand('sapBtpMcp.openSettings', () => {
            vscode.commands.executeCommand('workbench.action.openSettings', '@ext:sap-btp-mcp');
        })
    );

    // Command: run doctor
    disposables.push(
        vscode.commands.registerCommand('sapBtpMcp.runDoctor', async () => {
            const command = vscode.workspace.getConfiguration('sapBtpMcp').get<string>('command', 'sap-btp-agent');
            const terminal = vscode.window.createTerminal('SAP Doctor');
            terminal.show();
            terminal.sendText(`${quoteForShell(command)} doctor`);
        })
    );

    context.subscriptions.push(...disposables);
}

export function deactivate() { }
