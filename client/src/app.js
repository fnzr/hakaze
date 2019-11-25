import { PLATFORM } from "aurelia-framework";

export class App {
    message = 'Hello!';

    configureRouter(config, router) {
        this.router = router;
        config.title = 'Aurelia';
        config.map([
            { route: '', name: 'browser', moduleId: PLATFORM.moduleName('pages/browser'), title: 'Hakaze' },
        ]);
    }
}
