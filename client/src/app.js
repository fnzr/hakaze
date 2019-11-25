import { PLATFORM } from "aurelia-framework";

export class App {

    configureRouter(config, router) {
        this.router = router;
        config.map([
            { route: ['gallery/:dir'], name: 'gallery', moduleId: PLATFORM.moduleName('pages/gallery'), title: 'Hakaze' },
            { route: [''], name: 'browser', moduleId: PLATFORM.moduleName('pages/browser'), title: 'Hakaze' },
        ]);
    }
}
