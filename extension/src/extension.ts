import * as vscode from "vscode";
import { AuthStore } from "./auth";
import { analyzeActiveFile, analyzeEditorContent, handleCommandError } from "./commands/runner";
import { UnicornioPanelProvider } from "./panel/Provider";

export function activate(context: vscode.ExtensionContext): void {
  const auth = new AuthStore(context.secrets);
  const provider = new UnicornioPanelProvider(context.extensionUri, auth);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(UnicornioPanelProvider.viewType, provider),
    vscode.commands.registerCommand("unicornio.showPanel", async () => {
      await vscode.commands.executeCommand("unicornio.sidebar.focus");
    }),
    vscode.commands.registerCommand("unicornio.login", async () => {
      await vscode.commands.executeCommand("unicornio.sidebar.focus");
    }),
    vscode.commands.registerCommand("unicornio.logout", async () => {
      await auth.clearToken();
      vscode.window.showInformationMessage("Unicornio: sesión cerrada.");
    }),
    vscode.commands.registerCommand("unicornio.refactorSelection", async () => {
      try {
        await analyzeEditorContent(auth, "refactor");
      } catch (error) {
        await handleCommandError(error);
      }
    }),
    vscode.commands.registerCommand("unicornio.refactorFile", async () => {
      try {
        await analyzeActiveFile(auth, "refactor");
      } catch (error) {
        await handleCommandError(error);
      }
    }),
    vscode.commands.registerCommand("unicornio.auditFile", async () => {
      try {
        await analyzeActiveFile(auth, "security");
      } catch (error) {
        await handleCommandError(error);
      }
    }),
    vscode.commands.registerCommand("unicornio.performanceFile", async () => {
      try {
        await analyzeActiveFile(auth, "performance");
      } catch (error) {
        await handleCommandError(error);
      }
    }),
    vscode.commands.registerCommand("unicornio.debugSelection", async () => {
      const errorText = await vscode.window.showInputBox({
        prompt: "Describe el error",
        placeHolder: "KeyError: 'id'",
      });
      if (!errorText) {
        return;
      }
      try {
        await analyzeEditorContent(auth, "debug", { error: errorText });
      } catch (error) {
        await handleCommandError(error);
      }
    }),
  );
}

export function deactivate(): void {}
